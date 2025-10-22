# Test Azure Configuration Locally

Before pushing to Azure, test the docker-compose.azure.yml locally to ensure everything works.

## Step 1: Clean Up Previous Containers

```bash
# Stop and remove existing containers
docker-compose down -v
```

## Step 2: Build Azure Configuration Locally

```bash
# Build and start with azure config
docker-compose -f docker-compose.azure.yml build
docker-compose -f docker-compose.azure.yml up -d
```

## Step 3: Verify Services Running

```bash
# Check if all services are up
docker-compose -f docker-compose.azure.yml ps

# Expected output:
# NAME           STATUS
# rag-backend    Up (healthy)
# rag-frontend   Up
# ollama         Up (healthy)
```

## Step 4: Test Health Endpoints

```bash
# Frontend (should respond on port 80)
curl http://localhost/health

# Should return: {"status":"ok","service":"RAG-Backend"}

# Backend directly (on port 8000)
curl http://localhost:8000/health

# Should return: {"status":"ok","service":"RAG-Backend"}
```

## Step 5: Test Frontend Page

```bash
# Open in browser
# http://localhost/

# Check browser console for any errors
# API requests should go to /chat/ and /process_audio/
```

## Step 6: Test Chat Endpoint

```bash
# Send a chat request (will take 55+ seconds with Ollama)
curl -X POST http://localhost/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, what is AI?"}'

# Should stream responses and NOT timeout at 60 seconds
# (will timeout at 600 seconds / 10 minutes)
```

## Step 7: Check Logs

```bash
# Frontend logs (should show nginx serving on port 8080)
docker logs rag-frontend

# Backend logs (should show request processed)
docker logs rag-backend

# Ollama logs (should show model loaded and inference)
docker logs ollama
```

## Step 8: If Issues, Debug

```bash
# Frontend nginx config (generated from template)
docker exec rag-frontend cat /etc/nginx/conf.d/default.conf

# Should show:
# - listen 8080;
# - proxy_read_timeout 600s;
# - upstream backend { server backend:8000; }

# Test backend connectivity from frontend container
docker exec rag-frontend curl http://backend:8000/health

# Should return: {"status":"ok","service":"RAG-Backend"}
```

## Troubleshooting

### Port 80 Already in Use

```bash
# If you get "port 80 is already allocated"
# Change in docker-compose.azure.yml:
# ports:
#   - "8080:8080"  # Change from "80:8080"

# Then test on http://localhost:8080/
```

### Frontend not loading

```bash
# Check if nginx config was generated correctly
docker exec rag-frontend cat /etc/nginx/conf.d/default.conf

# Check nginx error logs
docker exec rag-frontend nginx -t

# Reload nginx
docker exec rag-frontend nginx -s reload
```

### Backend not responding

```bash
# Check backend logs
docker logs rag-backend -f

# Check if backend is listening
docker exec rag-backend lsof -i :8000

# Test manually
docker exec rag-backend curl http://localhost:8000/health
```

### Ollama not loaded

```bash
# Check ollama logs
docker logs ollama -f

# Check if model is pulled
docker exec ollama ollama list

# If model not there, manually pull
docker exec ollama ollama pull llama-guard3:1b
```

## Success Criteria

✅ All containers running and healthy  
✅ Frontend loads on http://localhost/  
✅ Health endpoint responds: http://localhost/health  
✅ Chat requests complete without timeout (even 55+ seconds)  
✅ No "upstream timed out" errors in logs  
✅ Nginx serving frontend + proxying to backend  

Once all tests pass, you're ready to push to Azure!

## What's Different in Azure vs Local?

| Item | Local | Azure |
|------|-------|-------|
| docker-compose | `docker-compose.yml` | `docker-compose.azure.yml` |
| Frontend port | 8080 | 80 (standard HTTP) |
| Build context | `Dockerfile` | `Dockerfile.azure` |
| Frontend base URL | `http://localhost:8080/` | `/` (relative) |
| Deployment method | `docker-compose up` | Azure Container Registry + ACI/App Service |

The timeout fixes (600s) are IDENTICAL in both configurations!
