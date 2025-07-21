# **Prerequisites**

Ensure the following tools are installed:

1. **Python 3.8+**: Download from [Python.org](https://www.python.org/downloads/).
2. **pip**: Python package manager (included with Python installations).
3. **Ollama**: Download and install from [Ollama official website](https://ollama.com/download)
4. **Docker**: Download and install from [Docker official website](https://www.docker.com/)

---

# **Setup Instructions**

### **1. Clone the Repository**
Use the following commands to clone the project repository and navigate into the project directory:

```bash
git clone repo_name
cd RAG_Embeddings
git checkout your-branch
```

---
# Setting Up a Python Virtual Environment

This guide provides step-by-step instructions on how to create and activate a Python virtual environment. Virtual environments are essential for managing package versions and ensuring that different projects can run in isolated settings without interfering with each other.

# Prerequisites

- Python 3.x installed on your machine. You can download Python from [python.org](https://www.python.org/downloads/).

## Creating a Virtual Environment

1. **Open your terminal or command prompt**.
2. **Navigate to your project directory** where you want the virtual environment to be set up.

    ```bash
    cd path/to/your/RAG_Embeddings
    ```

3. **Create the virtual environment**:
    - For **Windows**:
    
    ```bash
    python -m venv env
    ```

    - For **macOS and Linux**:
    
    ```bash
    python3 -m venv env
    ```

    This command will create a new directory called `env` within your project directory, where the virtual environment files will be stored.
---

## Activating the Virtual Environment

Once you have created a virtual environment, you need to activate it to use it.

- **On Windows**:

    ```bash
    .\env\Scripts\activate
    ```

- **On macOS and Linux**:

    ```bash
    source env/bin/activate
    ```



---
# Usage

```sh
python embedding.py --collection-name=docs_test --embedding-model=model_name --vectordb=vectordb --mode=mode
```
# Embedding modles
## ollama 
we only use this one
- nomic-embed-text

# Vector Stores:
- ChromaDB
# Collection names:
you should name the collections with these names
- turismo_native_chunk_750
- turismo_native_chunk_250
- turismo_full

# Mode:
this is to specify the size of the collections
- whole
- chunk250
- chunk750

---

# Run Ollama

- Download required models
```bash
  Ollama pull name-of-model
```
- List downloaded models
```bash
  Ollama list
```
- Run Ollama server
```bash
  Ollama serve
```
---

# Build Docker container
```bash
  docker compose build --no-cache && docker compose up -d

```

---
# Test APIs

```bash
curl -X POST http://host.docker.internal:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b",
    "prompt": "Your prompt here",
    "temperature": 0.5,
    "max_tokens": 100
}'

```

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b",
    "prompt": "Your prompt here",
    "temperature": 0.5,
    "max_tokens": 100
}'

```

# Test embedding:

```bash
curl -X POST http://host.docker.internal:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text:latest",
    "text": "Test input for embeddings"
}'

```
```bash
curl -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text:latest",

}'

```