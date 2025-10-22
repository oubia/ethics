import time
import logging
from src.utils.prompts.prompt import general_prompt
class LLMFactory:
    def __init__(self, model_name: str, system_prompt: str | None = None):
        self.model_name = model_name.lower()
        self.system_prompt = system_prompt or general_prompt
        if self.model_name == "llama":
            self.llm = self._init_llama_with_retry()
        else:
            raise ValueError(f"Unsupported model name: {model_name}. Supported models: 'llama'.")
    def _init_llama_with_retry(self):
        from langchain_ollama import OllamaLLM
        from src.config.settings import OLLAMA_LLM_ENDPOINT
        try:
            logging.info("Attempting to initialize Llama LLM at endpoint: %s", OLLAMA_LLM_ENDPOINT)
            llm = OllamaLLM(
                model="llama3.2:latest",  
                temperature=0.2,
                streaming=True,
                verbose=True,
                system=self.system_prompt,
                base_url=OLLAMA_LLM_ENDPOINT
            )
            logging.info("Llama LLM initialized successfully.")
            return llm
        except Exception as e:
            logging.error("Error initializing Llama LLM: %s", str(e))
            raise
    def get_llm(self):
        return self.llm

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import logging
import json

app = FastAPI()

# Assume llm_factory is initialized globally
from src.models.llm_factory import LLMFactory
llm_factory = LLMFactory("llama")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    try:
        llm = llm_factory.get_llm()
        
        async def generate():
            try:
                # Stream response with keepalive
                async for chunk in llm.astream(request.message):
                    # Send chunk as JSON
                    yield json.dumps({"content": chunk}) + "\n"
                    await asyncio.sleep(0)  # Yield control
                
                # Send completion signal
                yield json.dumps({"status": "completed"}) + "\n"
            except asyncio.CancelledError:
                logging.warning("Stream cancelled by client")
                yield json.dumps({"error": "Stream cancelled"}) + "\n"
            except Exception as e:
                logging.error("Stream error: %s", str(e))
                yield json.dumps({"error": str(e)}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
    except Exception as e:
        logging.error("Chat endpoint error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))