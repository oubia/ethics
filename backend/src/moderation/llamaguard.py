import requests
import os
from pathlib import Path
from src.config import settings

# Ollama endpoint and model config
OLLAMA_URL = os.getenv("OLLAMA_LLAMAGUARD_ENDPOINT", settings.OLLAMA_LLM_ENDPOINT)
LLAMAGUARD_MODEL = os.getenv("LLAMAGUARD_MODEL", "llama-guard3:1b")

# Path to policy file (mounted by docker-compose)
POLICY_PATH = Path("/app/docs/safety_policy.md")


def build_prompt(message: str, role: str, policy: str) -> str:
    """
    Build a moderation prompt. For 1B, output is simplified ("safe"/"unsafe").
    """
    return f"""
Sei Llama Guard. Devi classificare il seguente messaggio secondo la seguente politica di sicurezza.

Politica:
{policy}

Messaggio:
{message}

Rispondi SOLO con "safe" se è consentito, oppure "unsafe" se viola la politica.
    """


def run_llamaguard(message: str, role: str = "user") -> dict:
    """
    Call Llama Guard (1B version) via Ollama `/api/chat`.
    Interprets "safe"/"unsafe" into structured JSON verdict.
    """
    # Load safety policy (ignore if missing)
    if not POLICY_PATH.exists():
        return {
            "allowed": False,
            "categories": ["PolicyMissing"],
            "rationale": f"File di policy non trovato in {POLICY_PATH}"
        }

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        policy = f.read()

    prompt = build_prompt(message, role, policy)

    payload = {
        "model": LLAMAGUARD_MODEL,
        "messages": [
            {"role": "system", "content": "Sei un classificatore di sicurezza. Applica le regole fornite"},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0},
        "stream": False
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        #print("(DEBUG: LLAAMA-GUARD MODERATION RESPONSE:", data)

        # Extract response text
        text = data.get("message", {}).get("content", "").strip().lower()
        #print("DEBUG: RAW RESPONSE:", text)

        # Interpret safe/unsafe
        if "safe" in text and "unsafe" not in text:
            return {
                "allowed": True,
                "categories": [],
                "rationale": "Classificato come SICURO dal modello (1B)"
            }

        if "unsafe" in text:
            return {
                "allowed": False,
                "categories": ["NON SICURO"],
                "rationale": "Classificato come NON SICURO dal modello (1B)"
            }

        # Fallback if not recognized
        return {
            "allowed": False,
            "categories": ["Unrecognized"],
            "rationale": f"Output non riconosciuto: {text}"
        }

    except requests.exceptions.RequestException as e:
        return {"allowed": False, "categories": ["NetworkError"], "rationale": str(e)}