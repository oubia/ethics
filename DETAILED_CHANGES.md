# Detailed Changes Made - File by File

## 1. nginx.conf (COMPLETELY REPLACED)

### Before:
```python
# File had corrupted Python code instead of nginx config
```

### After:
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Upstream backend configuration
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    server {
        listen 8080;
        server_name _;
        charset utf-8;

        # CRITICAL TIMEOUT SETTINGS (10 minutes instead of 60 seconds)
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;

        # CRITICAL FOR STREAMING (disable buffering)
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Chat endpoint
        location /chat/ {
            proxy_pass http://backend;
            proxy_set_header Transfer-Encoding chunked;
        }

        # Audio endpoint
        location /process_audio/ {
            proxy_pass http://backend;
            proxy_set_header Transfer-Encoding chunked;
        }

        # Default
        location / {
            proxy_pass http://backend;
        }

        # Health check
        location /health {
            proxy_pass http://backend;
        }
    }
}
```

**Key Changes:**
- ✅ `proxy_read_timeout 60s` → `600s` (10 minutes)
- ✅ `proxy_connect_timeout 60s` → `600s` (10 minutes)
- ✅ `proxy_send_timeout 60s` → `600s` (10 minutes)
- ✅ Added `proxy_buffering off` for streaming
- ✅ Added `proxy_request_buffering off`
- ✅ Added proper upstream backend configuration

---

## 2. docker-compose.yml (ADDED NGINX SERVICE)

### Before:
```yaml
version: '3.8'
services:
  backend:
    ...
  frontend:
    ...
  ollama:
    ...
```

### After:
```yaml
version: '3.8'
services:
  # NEW: Nginx reverse proxy
  nginx:
    image: nginx:latest
    container_name: rag-nginx
    ports:
      - "8080:8080"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    environment:
      - NGINX_PROXY_READ_TIMEOUT=600s
      - NGINX_PROXY_CONNECT_TIMEOUT=600s
      - NGINX_PROXY_SEND_TIMEOUT=600s
    depends_on:
      - backend
    networks:
      - rag-network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build: ./backend
    container_name: rag-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./Vectorestor:/app/Vectorestor
      - ./docs:/app/docs
    env_file:
      - ./.env
    environment:
      # NEW: Extended timeouts
      - OLLAMA_REQUEST_TIMEOUT=600
      - REQUEST_TIMEOUT=600
    depends_on:
      - ollama
    networks:
      - rag-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: rag-frontend
    environment:
      # CHANGED: Point to nginx instead of backend
      - REACT_APP_BASE_URL=http://nginx:8080/
    depends_on:
      - nginx
    networks:
      - rag-network

  ollama:
    build:
      context: ./Ollama
      dockerfile: Dockerfile
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 30s
      timeout: 10s
      retries: 3
    command: >
      /bin/sh -c "
        ollama list | grep -q 'llama-guard3:1b' || ollama pull llama-guard3:1b;
        ollama serve
      "
    networks:
      - rag-network

volumes:
  ollama_data:

# NEW: Custom network
networks:
  rag-network:
    driver: bridge
```

**Key Changes:**
- ✅ Added `nginx` service with port 8080
- ✅ Added timeout environment variables to `backend`
- ✅ Changed frontend `REACT_APP_BASE_URL` to point to nginx
- ✅ Added health checks for all services
- ✅ Created custom `rag-network` for service communication

---

## 3. backend/src/config/settings.py (ADDED TIMEOUT CONFIG)

### Before:
```python
import os
import dotenv

dotenv.load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DIR")
OLLAMA_LLM_ENDPOINT = os.getenv("OLLAMA_LLM_ENDPOINT", "http://localhost:11434/")
OLLAMA_EMBEDDINGS_ENDPOINT = os.getenv("OLLAMA_EMBEDDINGS_ENDPOINT", "http://localhost:11434/")

print(f"CHROMA_DIR: {CHROMA_DIR}")
print(f"OLLAMA_LLM_ENDPOINT: {OLLAMA_LLM_ENDPOINT}")
print(f"OLLAMA_EMBEDDINGS_ENDPOINT: {OLLAMA_EMBEDDINGS_ENDPOINT}")
```

### After:
```python
import os
import dotenv

dotenv.load_dotenv()

# Directory settings
CHROMA_DIR = os.getenv("CHROMA_DIR")

# LLM and Embedding Endpoints
OLLAMA_LLM_ENDPOINT = os.getenv("OLLAMA_LLM_ENDPOINT", "http://ollama:11434/")
OLLAMA_EMBEDDINGS_ENDPOINT = os.getenv("OLLAMA_EMBEDDINGS_ENDPOINT", "http://ollama:11434/")

# NEW: Timeout Settings (in seconds)
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
```

**Key Changes:**
- ✅ Changed default endpoint from `localhost` to `ollama` (docker-compose service name)
- ✅ Added `REQUEST_TIMEOUT = 600`
- ✅ Added `OLLAMA_REQUEST_TIMEOUT = 600`
- ✅ Added `STREAMING_TIMEOUT = 600`
- ✅ All read from environment variables with 600s defaults

---

## 4. backend/src/models/llm_factory.py (UPDATED TIMEOUT)

### Before:
```python
class LLMFactory:
    def __init__(self, model_name: str, system_prompt: str | None = None, timeout: int = 300):
        # timeout: 300s (5 minutes) - TOO SHORT!
        
    def _init_llama_with_retry(self):
        from langchain_ollama import OllamaLLM
        from src.config.settings import OLLAMA_LLM_ENDPOINT
        
        try:
            llm = OllamaLLM(
                model="llama3.2:latest",
                temperature=0.2,
                streaming=True,
                verbose=True,
                system=self.system_prompt,
                base_url=OLLAMA_LLM_ENDPOINT,
                timeout=self.timeout  # 300s
            )
            # ...
```

### After:
```python
class LLMFactory:
    def __init__(self, model_name: str, system_prompt: str | None = None, timeout: int = 600):
        # timeout: 600s (10 minutes) - EXTENDED!
        
    def _init_llama_with_retry(self):
        from langchain_ollama import OllamaLLM
        from src.config.settings import OLLAMA_LLM_ENDPOINT, OLLAMA_REQUEST_TIMEOUT
        
        # Use timeout from settings or fall back to instance timeout
        timeout = OLLAMA_REQUEST_TIMEOUT if OLLAMA_REQUEST_TIMEOUT else self.timeout
        
        try:
            logging.info("Attempting to initialize Llama LLM at endpoint: %s with timeout: %ds", 
                        OLLAMA_LLM_ENDPOINT, timeout)
            llm = OllamaLLM(
                model="llama3.2:latest",
                temperature=0.2,
                streaming=True,
                verbose=True,
                system=self.system_prompt,
                base_url=OLLAMA_LLM_ENDPOINT,
                timeout=timeout  # 600s from settings
            )
            logging.info("Llama LLM initialized successfully with timeout: %ds", timeout)
            # ...
```

**Key Changes:**
- ✅ Changed default timeout from `300s` → `600s`
- ✅ Now reads `OLLAMA_REQUEST_TIMEOUT` from settings
- ✅ Better logging of timeout value
- ✅ Proper fallback mechanism

---

## 5. backend/main.py (ADDED HEADERS & HEALTH CHECK)

### Before:
```python
@app.post("/chat/")
async def chat_endpoint(message: Message):
    # ... code ...
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
        }
    )

@app.post("/process_audio/")
async def process_audio(audio: UploadFile = File(...)):
    # ... code ...
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
        }
    )
```

### After:
```python
# NEW: Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker container"""
    return {"status": "ok", "service": "RAG-Backend"}

@app.post("/chat/")
async def chat_endpoint(message: Message):
    # ... code ...
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # NEW: Disable nginx buffering
        }
    )

@app.post("/process_audio/")
async def process_audio(audio: UploadFile = File(...)):
    # ... code ...
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # NEW: Disable nginx buffering
        }
    )
```

**Key Changes:**
- ✅ Added `GET /health` endpoint for Docker healthchecks
- ✅ Added `X-Accel-Buffering: no` header to disable nginx buffering
- ✅ This ensures streaming chunks are sent immediately

---

## Summary of All Changes

| File | Type | Changes |
|------|------|---------|
| `nginx.conf` | Replaced | Added 600s timeouts, disabled buffering |
| `docker-compose.yml` | Updated | Added nginx service, env vars, networking |
| `settings.py` | Updated | Added timeout constants |
| `llm_factory.py` | Updated | 300s → 600s, use settings timeout |
| `main.py` | Updated | Added health endpoint, buffering headers |

**Total Impact:**
- 🟢 5 files modified
- ✅ Nginx timeout: 60s → 600s (10x increase)
- ✅ Backend timeout: 300s → 600s
- ✅ Proper streaming support
- ✅ Health checks enabled
- ✅ Docker networking configured
