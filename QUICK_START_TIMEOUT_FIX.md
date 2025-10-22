# Quick Start - After Timeout Fix

## 1. Rebuild and Deploy

```bash
cd d:\homy\Boss fight\Ethics\ethics

# Stop existing containers
docker-compose down

# Remove old volumes if needed (optional)
# docker volume prune

# Rebuild images
docker-compose build

# Start services
docker-compose up -d
```

## 2. Verify Services Are Running

```bash
# Check all containers
docker-compose ps

# Expected output:
# NAME              STATUS
# rag-nginx         Up (healthy)
# rag-backend       Up (healthy)
# ollama            Up (healthy)
```

## 3. Check Health Endpoints

```bash
# Nginx proxy
curl http://localhost:8080/health

# Backend directly
curl http://localhost:8000/health

# Should return: {"status":"ok","service":"RAG-Backend"}
```

## 4. Test Chat Endpoint

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, what is Python?",
    "selectedapproach": "your_approach",
    "selectedChunkSize": 512,
    "selectedapproachRetriever": "your_retriever"
  }'
```

## 5. Monitor Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rag-backend
docker-compose logs -f rag-nginx
docker-compose logs -f ollama
```

## 6. Key Indicators the Fix is Working

✅ **In nginx logs**, you should see:
- Request processed successfully
- No "upstream timed out" errors
- Response times 50-60+ seconds (depending on model)

✅ **In backend logs**, you should see:
- Streaming response being sent
- No timeout exceptions
- Chunks being yielded

✅ **In frontend browser**, you should see:
- Chat response appearing and streaming
- No timeout error after 60 seconds
- Complete response delivered

## 7. Frontend Connection

Make sure frontend's environment variable points to nginx:
```javascript
// Frontend should connect to:
http://localhost:8080/  // nginx proxy (NEW)

// NOT directly to backend:
http://localhost:8000/  // (OLD - avoid)
```

## 8. Troubleshooting

### Still getting timeout errors?
1. Check docker-compose.yml has all services with proper timeouts
2. Verify nginx.conf was updated with 600s timeouts
3. Check backend settings.py has OLLAMA_REQUEST_TIMEOUT=600
4. Review llm_factory.py timeout settings

### Response very slow?
1. Check Ollama is loaded: `docker logs ollama | grep "model"`
2. Check system resources: `docker stats`
3. Monitor backend processing: `docker logs rag-backend`

### 502/503 errors?
1. Check backend health: `curl http://localhost:8000/health`
2. Check nginx logs: `docker-compose logs rag-nginx`
3. Verify backend is running: `docker-compose ps`

## 9. Environment Variables (In docker-compose.yml)

```yaml
backend:
  environment:
    - OLLAMA_REQUEST_TIMEOUT=600      # 10 minutes
    - REQUEST_TIMEOUT=600              # 10 minutes
```

These can be overridden by passing to `docker-compose`:
```bash
OLLAMA_REQUEST_TIMEOUT=900 docker-compose up
```

## 10. Accessing the Application

- **Frontend**: http://localhost:3000 (if running locally)
- **Backend API**: http://localhost:8080/ (via nginx)
- **Ollama API**: http://localhost:11434 (internal only)

---

✅ **All fixes have been applied!** The timeout issue should now be resolved.
