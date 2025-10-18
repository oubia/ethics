import os
import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()
CHROMA_DIR = os.getenv("CHROMA_DIR")
OLLAMA_LLM_ENDPOINT = os.getenv("OLLAMA_LLM_ENDPOINT", "http://localhost:11434/")
OLLAMA_EMBEDDINGS_ENDPOINT = os.getenv("OLLAMA_EMBEDDINGS_ENDPOINT", "http://localhost:11434/")


print(f"CHROMA_DIR: {CHROMA_DIR}")
print(f"OLLAMA_LLM_ENDPOINT: {OLLAMA_LLM_ENDPOINT}")
print(f"OLLAMA_EMBEDDINGS_ENDPOINT: {OLLAMA_EMBEDDINGS_ENDPOINT}")