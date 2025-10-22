import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Directory settings
CHROMA_DIR = os.getenv("CHROMA_DIR")

# LLM and Embedding Endpoints
OLLAMA_LLM_ENDPOINT = os.getenv("OLLAMA_LLM_ENDPOINT", "http://ollama:11434/")
OLLAMA_EMBEDDINGS_ENDPOINT = os.getenv("OLLAMA_EMBEDDINGS_ENDPOINT", "http://ollama:11434/")

# Timeout Settings (in seconds)
# These ensure long-running requests don't timeout prematurely
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "600"))  # 10 minutes
OLLAMA_REQUEST_TIMEOUT = int(os.getenv("OLLAMA_REQUEST_TIMEOUT", "600"))  # 10 minutes
STREAMING_TIMEOUT = int(os.getenv("STREAMING_TIMEOUT", "600"))  # 10 minutes

# Logging
print(f"CHROMA_DIR: {CHROMA_DIR}")
print(f"OLLAMA_LLM_ENDPOINT: {OLLAMA_LLM_ENDPOINT}")
print(f"OLLAMA_EMBEDDINGS_ENDPOINT: {OLLAMA_EMBEDDINGS_ENDPOINT}")
print(f"REQUEST_TIMEOUT: {REQUEST_TIMEOUT}s")
print(f"OLLAMA_REQUEST_TIMEOUT: {OLLAMA_REQUEST_TIMEOUT}s")