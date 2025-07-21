import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DIR", "./Vectorestor")

OLLAMA_EMBEDDINGS_ENDPOINT = "http://localhost:11434/"

print(f"\n \n \n ollama endpoint: {OLLAMA_EMBEDDINGS_ENDPOINT}        \n chromadb path: {CHROMA_DIR}  ")
