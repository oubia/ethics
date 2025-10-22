# All-in-One Deployment Guide

The **all-in-one** approach combines all services (Frontend, Backend, Ollama) in a single Docker container optimized for Azure App Service and simple deployments.

## Overview

✅ **Single Container** - All services in one image  
✅ **Nginx Frontend** - Serves React app on port 3000  
✅ **FastAPI Backend** - REST API on port 8000 (internal)  
✅ **Ollama LLM** - Model inference on port 11434 (internal)  
✅ **Supervisor** - Manages all processes with auto-restart  
✅ **600s Timeouts** - Configured everywhere for long-running LLM requests  

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Single Docker Container: ethics-allinone       │
├─────────────────────────────────────────────────┤
│  Supervisor (Process Manager)                   │
│  ├─ Priority 1: Ollama (starts first)           │
│  ├─ Priority 999: Nginx (frontend proxy)        │
│  └─ Priority 999: FastAPI (waits for Ollama)    │
├─────────────────────────────────────────────────┤
│  Nginx (port 3000)                              │
│  ├─ Serves React frontend                       │
│  ├─ Proxies /chat/ → FastAPI:8000               │
│  ├─ Proxies /process_audio/ → FastAPI:8000      │
│  ├─ Proxies /api/ → FastAPI:8000                │
│  └─ All timeouts: 600s (10 min)                 │
├─────────────────────────────────────────────────┤
│  FastAPI (port 8000, internal)                  │
│  ├─ REST API endpoints                          │
│  ├─ Streaming responses                         │
│  ├─ PYTHONPATH=/app/backend/src                 │
│  └─ Timeout: REQUEST_TIMEOUT=600s               │
├─────────────────────────────────────────────────┤
│  Ollama (port 11434, internal)                  │
│  ├─ Llama 3.2 3B Instruct model                 │
│  └─ Timeout: OLLAMA_REQUEST_TIMEOUT=600s        │
└─────────────────────────────────────────────────┘
```

## Port Mapping

| Service | Internal | External | Purpose |
|---------|----------|----------|---------|
| Nginx | 3000 | 3000 | React frontend + API proxy |
| FastAPI | 8000 | 8000 | Backend API (debug only) |
| Ollama | 11434 | 11434 | LLM server (debug only) |

## Quick Start

### Local Testing (Windows PowerShell)

```bash
# Navigate to project
cd "d:\homy\Boss fight\Ethics\ethics"

# Build image
docker build -f Dockerfile.allinone -t ethics-allinone .

# Run with docker-compose
docker-compose -f docker-compose.allinone.yml up -d

# Check all services running
docker-compose -f docker-compose.allinone.yml ps
# Expected: ethics-app UP (healthy)

# View real-time logs
docker-compose -f docker-compose.allinone.yml logs -f app

# Stop
docker-compose -f docker-compose.allinone.yml down
```

### Test Endpoints

```bash
# Frontend (should load React app)
curl http://localhost:3000/

# Health check
curl http://localhost:3000/health
# Response: {"status":"ok","service":"RAG-Backend"}

# Chat endpoint (55+ seconds, should NOT timeout)
$body = @{message="What is AI ethics?"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:3000/chat/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body

# Verify: Response completes without "upstream timed out" errors
```

## Startup Sequence

Supervisor starts services in priority order:

1. **Ollama (Priority 1)** - Starts immediately
   - Loads Llama 3.2 3B model into memory
   - Ready on http://localhost:11434
   - ⏱️ ~30-60 seconds first startup

2. **Nginx + FastAPI (Priority 999)** - Start together
   - FastAPI waits 5 seconds for Ollama readiness
   - Nginx serves frontend immediately
   - ⏱️ Ready in ~10 seconds

**Total startup time:** ~45-75 seconds

```bash
# Check process status
docker exec ethics-app supervisorctl status

# Expected output:
# nginx                            RUNNING   pid 12, uptime 0:01:05
# ollama                           RUNNING   pid 45, uptime 0:01:03
# fastapi                          RUNNING   pid 78, uptime 0:00:58
```

## Environment Variables

All pre-configured for 600s (10-minute) timeouts:

```
PYTHONPATH=/app/backend/src              # Python module path
CHROMA_DIR=/app/Vectorestor              # Vector store location
OLLAMA_LLM_ENDPOINT=http://localhost:11434/        # Ollama server
OLLAMA_EMBEDDINGS_ENDPOINT=http://localhost:11434/ # Embeddings
REQUEST_TIMEOUT=600                      # FastAPI timeout (seconds)
OLLAMA_REQUEST_TIMEOUT=600                # Ollama timeout (seconds)
STREAMING_TIMEOUT=600                    # Streaming timeout (seconds)
```

## Nginx Configuration

**Timeouts (All set to 600s = 10 minutes):**
```
proxy_connect_timeout 600s;    # Connection establishment
proxy_send_timeout 600s;       # Request sending
proxy_read_timeout 600s;       # Response reading
```

**Streaming Support (No buffering):**
```
proxy_buffering off;           # Disable response buffering
proxy_request_buffering off;   # Disable request buffering
proxy_http_version 1.1;        # Keep-alive connections
```

**Routes:**
- `/ ` → React frontend (`/app/frontend/build`)
- `/chat/` → FastAPI backend (streaming, 600s timeout)
- `/process_audio/` → FastAPI backend (streaming, 600s timeout)
- `/health` → Health check endpoint
- `/api/` → REST API endpoints

## Local Deployment

### Step 1: Build Image

```bash
cd "d:\homy\Boss fight\Ethics\ethics"
docker build -f Dockerfile.allinone -t ethics-allinone:latest .
```

Wait for build to complete (2-3 minutes).

### Step 2: Run with Docker Compose

```bash
docker-compose -f docker-compose.allinone.yml build
docker-compose -f docker-compose.allinone.yml up -d
```

### Step 3: Wait for Startup

```bash
# Wait ~60 seconds for Ollama to load model
Start-Sleep -Seconds 60

# Check all services running
docker-compose -f docker-compose.allinone.yml ps
```

Expected:
```
NAME              STATUS              PORTS
ethics-app        Up (healthy)        0.0.0.0:3000->3000/tcp, 0.0.0.0:8000->8000/tcp, 0.0.0.0:11434->11434/tcp
```

### Step 4: Access Application

- **Frontend:** http://localhost:3000/
- **API Direct:** http://localhost:8000/health

### Step 5: Test Long-Running Request

```bash
# This takes 55+ seconds - verify it completes!
curl -X POST http://localhost:3000/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message":"Explain ethical AI principles"}'
```

Should stream response without timeout.

### Step 6: View Logs

```bash
# All services
docker logs ethics-app -f

# Specific logs
docker exec ethics-app tail -f /var/log/supervisor/nginx.out.log
docker exec ethics-app tail -f /var/log/supervisor/fastapi.out.log
docker exec ethics-app tail -f /var/log/supervisor/ollama.out.log

# Check processes
docker exec ethics-app ps aux | grep -E "nginx|ollama|uvicorn"
```

## Azure Deployment

### Step 1: Build and Push to Registry

```bash
# Login to Azure Container Registry
az acr login --name ethicsacr

# Build image
docker build -f Dockerfile.allinone -t ethicsacr.azurecr.io/ethics-allinone:latest .

# Push to Azure Registry
docker push ethicsacr.azurecr.io/ethics-allinone:latest
```

### Step 2: Deploy to Azure Container Instances

```bash
az container create `
  --resource-group ethics-rg `
  --name ethics-allinone `
  --image ethicsacr.azurecr.io/ethics-allinone:latest `
  --registry-login-server ethicsacr.azurecr.io `
  --registry-username ethicsacr `
  --registry-password <PASSWORD> `
  --cpu 2 `
  --memory 4 `
  --ports 3000 8000 11434 `
  --environment-variables `
    PYTHONPATH=/app/backend/src `
    CHROMA_DIR=/app/Vectorestor `
    OLLAMA_LLM_ENDPOINT=http://localhost:11434/ `
    OLLAMA_EMBEDDINGS_ENDPOINT=http://localhost:11434/ `
    REQUEST_TIMEOUT=600 `
    OLLAMA_REQUEST_TIMEOUT=600 `
    STREAMING_TIMEOUT=600
```

### Step 3: Get Container IP

```bash
az container show --resource-group ethics-rg --name ethics-allinone `
  --query ipAddress.ip --output tsv
```

### Step 4: Access Application

```bash
# Replace <IP> with output from Step 3
https://<IP>:3000/
```

### Step 5: Monitor Logs

```bash
# Real-time logs
az container logs --resource-group ethics-rg --name ethics-allinone -f

# Check specific service
az container attach --resource-group ethics-rg --name ethics-allinone
```

## Troubleshooting

### Container won't start

```bash
# Check build output for errors
docker build -f Dockerfile.allinone -t ethics-allinone . --no-cache

# Check container logs
docker logs ethics-app

# Common issues:
# - PORT 3000 already in use: docker ps to find and kill
# - Out of memory: Ensure 4GB+ available
# - Python import errors: Check backend/requirements.txt
```

### Services not running

```bash
# Check supervisor status
docker exec ethics-app supervisorctl status

# Expected: All services RUNNING

# If service crashed, restart it
docker exec ethics-app supervisorctl restart nginx
docker exec ethics-app supervisorctl restart fastapi
docker exec ethics-app supervisorctl restart ollama

# View supervisor logs
docker exec ethics-app tail -f /var/log/supervisor/supervisord.log
```

### Nginx not proxying requests

```bash
# Verify nginx config generated correctly
docker exec ethics-app cat /etc/nginx/conf.d/frontend.conf

# Should show: upstream backend { server localhost:8000; }

# Test nginx syntax
docker exec ethics-app nginx -t
# Should show: "syntax is ok"

# Reload nginx
docker exec ethics-app nginx -s reload

# Test backend connectivity
docker exec ethics-app curl http://localhost:8000/health
```

### Backend not responding

```bash
# Check FastAPI logs
docker exec ethics-app tail -f /var/log/supervisor/fastapi.out.log

# Check if uvicorn is running
docker exec ethics-app ps aux | grep uvicorn

# Test directly
docker exec ethics-app curl http://localhost:8000/health

# Check PYTHONPATH is correct
docker exec ethics-app env | grep PYTHONPATH
# Should show: PYTHONPATH=/app/backend/src
```

### Ollama not loaded

```bash
# Check Ollama logs
docker exec ethics-app tail -f /var/log/supervisor/ollama.out.log

# Check if ollama is running
docker exec ethics-app ps aux | grep ollama

# List available models
docker exec ethics-app ollama list

# Check model status
docker exec ethics-app curl http://localhost:11434/api/tags
```

### Chat requests timing out

```bash
# Verify nginx has 600s timeout
docker exec ethics-app grep "proxy_read_timeout" /etc/nginx/conf.d/frontend.conf
# Should show: proxy_read_timeout 600s;

# Verify backend timeout
docker exec ethics-app env | grep TIMEOUT
# Should show:
# REQUEST_TIMEOUT=600
# OLLAMA_REQUEST_TIMEOUT=600
# STREAMING_TIMEOUT=600

# Check response headers
curl -v http://localhost:3000/health 2>&1 | grep -i timeout
```

## Success Checklist

Before pushing to Azure, verify locally:

✅ Docker image builds without errors  
```bash
docker build -f Dockerfile.allinone -t ethics-allinone . 2>&1 | tail -5
# Should show: "Successfully tagged ethics-allinone:latest"
```

✅ Container starts and stays running  
```bash
docker-compose -f docker-compose.allinone.yml up -d
sleep 10
docker-compose -f docker-compose.allinone.yml ps
# Should show: ethics-app UP (healthy)
```

✅ All supervisor processes running  
```bash
docker exec ethics-app supervisorctl status
# Should show nginx, fastapi, ollama all RUNNING
```

✅ Nginx serves frontend  
```bash
curl http://localhost:3000/ | grep -i react
# Should return HTML with React app
```

✅ Health endpoint responds  
```bash
curl http://localhost:3000/health
# Should return: {"status":"ok","service":"RAG-Backend"}
```

✅ Chat endpoint works and doesn't timeout  
```bash
# This takes 55+ seconds - verify it completes!
time curl -X POST http://localhost:3000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"What is AI?"}'
# Should complete with response (NOT timeout after 60 seconds)
```

✅ No "upstream timed out" errors in logs  
```bash
docker logs ethics-app 2>&1 | grep -i timeout
# Should return nothing (no timeout errors)
```

## Performance Notes

### Memory Usage
- **Ollama (LLM):** ~2GB (3B model loaded)
- **FastAPI:** ~500MB
- **Nginx:** ~50MB
- **Total:** ~2.5-3GB

Ensure Azure container has 4GB RAM minimum.

### Startup Time
- **Ollama model load:** 30-60 seconds (first startup)
- **Nginx + FastAPI:** 10 seconds
- **Total:** ~45-75 seconds
- **Note:** Subsequent requests are fast (2-5s)

### First Request vs Subsequent
- **First request:** 55+ seconds (model in memory, inference running)
- **Subsequent requests:** 2-5 seconds (model cached)

## Files Modified

| File | Change |
|------|--------|
| `Dockerfile.allinone` | Updated supervisor config with proper priorities and timeouts |
| `docker-compose.allinone.yml` | All environment variables configured |
| `backend/Dockerfile` | (unchanged - uses Dockerfile.allinone) |
| `frontend/Dockerfile` | (unchanged - built into Dockerfile.allinone) |

## What's NOT Included

- `docker-compose.azure.yml` (removed - use allinone)
- `frontend/Dockerfile.azure` (removed - use allinone)
- Separate nginx service (removed - nginx in allinone)

## Key Configuration Points

### Supervisor Process Order

```
Priority 1:  Ollama (starts first, model loading)
Priority 999: Nginx (frontend serving)
Priority 999: FastAPI (waits 5s for Ollama, then starts)
```

### Environment Variables in Supervisor

FastAPI process receives:
```
PYTHONPATH=/app/backend/src
CHROMA_DIR=/app/Vectorestor
OLLAMA_LLM_ENDPOINT=http://localhost:11434/
OLLAMA_EMBEDDINGS_ENDPOINT=http://localhost:11434/
REQUEST_TIMEOUT=600
OLLAMA_REQUEST_TIMEOUT=600
STREAMING_TIMEOUT=600
```

### Nginx Timeouts

All proxy operations have 600s (10-minute) timeouts:
```
proxy_connect_timeout 600s
proxy_send_timeout 600s
proxy_read_timeout 600s
```

Streaming support enabled:
```
proxy_buffering off
proxy_request_buffering off
proxy_http_version 1.1
```

## Deployment Summary

| Step | Local | Azure |
|------|-------|-------|
| Build | `docker build -f Dockerfile.allinone .` | Same |
| Push | N/A | `docker push ethicsacr.azurecr.io/...` |
| Run | `docker-compose -f docker-compose.allinone.yml up` | Azure Container Instances / App Service |
| Access | http://localhost:3000 | https://<container-ip>:3000 |

## Next Steps

1. ✅ **Test Locally**
   ```bash
   docker-compose -f docker-compose.allinone.yml up -d
   curl http://localhost:3000/health
   ```

2. ✅ **Verify All Services**
   ```bash
   docker exec ethics-app supervisorctl status
   ```

3. ✅ **Push to GitHub**
   ```bash
   git add Dockerfile.allinone docker-compose.allinone.yml
   git commit -m "All-in-one deployment ready"
   git push origin main
   ```

4. ✅ **Push to Azure Registry**
   ```bash
   docker push ethicsacr.azurecr.io/ethics-allinone:latest
   ```

5. ✅ **Deploy to Azure Container Instances**
   - Follow Step 2 under "Azure Deployment" section above

## Support

If you encounter issues:

1. Check logs: `docker logs ethics-app -f`
2. Check processes: `docker exec ethics-app supervisorctl status`
3. Test individually: `docker exec ethics-app curl http://localhost:8000/health`
4. Review this guide's troubleshooting section

**All-in-one is production-ready for Azure! 🚀**

  -p 8000:8000 \
  -p 11434:11434 \
  -v ./Vectorestor:/app/Vectorestor \
  -v ./backend:/app/backend \
  -e PYTHONPATH=src \
  -e CHROMA_DIR=/app/Vectorestor \
  -e OLLAMA_LLM_ENDPOINT=http://localhost:11434/ \
  -e OLLAMA_EMBEDDINGS_ENDPOINT=http://localhost:11434/ \
  -e REQUEST_TIMEOUT=600 \
  -e OLLAMA_REQUEST_TIMEOUT=600 \
  -e STREAMING_TIMEOUT=600 \
  ethics-allinone

# View logs
docker logs ethics-app -f
```

## Access Application

### Frontend
```
http://localhost:3000/
```

### Backend Health Check
```
http://localhost:8000/health
```

### Backend Swagger Docs
```
http://localhost:8000/docs
```

### Ollama Models
```
http://localhost:11434/api/tags
```

## Testing

### 1. Frontend Health

```bash
curl http://localhost:3000/health
```

Response: `{"status":"ok","service":"RAG-Backend"}`

### 2. Backend Health

```bash
curl http://localhost:8000/health
```

Response: `{"status":"ok","service":"RAG-Backend"}`

### 3. Chat Request (Long-Running)

```bash
curl -X POST http://localhost:3000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain machine learning"}'
```

Expected: Streams response for 55+ seconds without timeout.

### 4. Verify All Services Running

```bash
docker exec ethics-app supervisorctl status

# Expected:
# nginx         RUNNING   pid 123, uptime 1:00:00
# fastapi       RUNNING   pid 124, uptime 1:00:00
# ollama        RUNNING   pid 125, uptime 1:00:00
```

## Timeout Configuration

All components set to **600 seconds (10 minutes)**:

| Component | Setting | Value |
|-----------|---------|-------|
| Nginx read timeout | proxy_read_timeout | 600s |
| Nginx connect timeout | proxy_connect_timeout | 600s |
| Nginx send timeout | proxy_send_timeout | 600s |
| Backend request timeout | REQUEST_TIMEOUT | 600s |
| Ollama timeout | OLLAMA_REQUEST_TIMEOUT | 600s |

This ensures requests up to 10 minutes complete without timing out.

## Nginx Configuration

Frontend on port 3000 routes traffic:

```
GET http://localhost:3000/              → React frontend (index.html, CSS, JS)
POST http://localhost:3000/chat/        → Backend (port 8000/chat/)
POST http://localhost:3000/process_audio/ → Backend (port 8000/process_audio/)
GET http://localhost:3000/health        → Backend (port 8000/health)
GET http://localhost:3000/api/*         → Backend (port 8000/api/*)
```

All proxy connections have:
- `proxy_buffering off` - Stream responses immediately
- `proxy_request_buffering off` - Stream requests immediately
- 600s timeouts on all operations

## Environment Variables

Inside the container:

```env
PYTHONPATH=src
CHROMA_DIR=/app/Vectorestor
OLLAMA_LLM_ENDPOINT=http://localhost:11434/
OLLAMA_EMBEDDINGS_ENDPOINT=http://localhost:11434/
REQUEST_TIMEOUT=600
OLLAMA_REQUEST_TIMEOUT=600
STREAMING_TIMEOUT=600
```

These are set in `docker-compose.allinone.yml` and passed to FastAPI via Supervisor.

## Logging

### View Container Logs

```bash
docker-compose -f docker-compose.allinone.yml logs -f app
```

### Inside Container

```bash
# Nginx
docker exec ethics-app cat /var/log/supervisor/nginx.out.log

# FastAPI
docker exec ethics-app cat /var/log/supervisor/fastapi.out.log

# Ollama
docker exec ethics-app cat /var/log/supervisor/ollama.out.log

# All supervisor logs
docker exec ethics-app cat /var/log/supervisor/supervisord.log
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs ethics-app

# Common issues:
# 1. Port already in use: docker ps | grep 3000
# 2. Dockerfile build error: docker build -f Dockerfile.allinone . --no-cache
# 3. Check Supervisor config: docker exec ethics-app supervisord -c /etc/supervisor/conf.d/supervisord.conf
```

### Nginx Not Proxying

```bash
# Check nginx config
docker exec ethics-app cat /etc/nginx/conf.d/frontend.conf

# Test nginx syntax
docker exec ethics-app nginx -t

# Reload nginx
docker exec ethics-app nginx -s reload
```

### Backend Not Responding

```bash
# Check if FastAPI is running
docker exec ethics-app supervisorctl status fastapi

# Restart FastAPI
docker exec ethics-app supervisorctl restart fastapi

# Test directly
docker exec ethics-app curl http://localhost:8000/health
```

### Ollama Model Not Loaded

```bash
# Check loaded models
docker exec ethics-app ollama list

# If model not there, pull manually (takes 5-10 min, 1.87 GiB)
docker exec ethics-app ollama pull llama-guard3:1b

# Check Ollama status
docker exec ethics-app curl http://localhost:11434/api/tags
```

### Chat Request Timing Out

```bash
# Verify timeout in config
docker exec ethics-app cat /etc/nginx/conf.d/frontend.conf | grep timeout

# Should show: proxy_read_timeout 600s;
# If not, rebuild: docker build -f Dockerfile.allinone . --no-cache
```

## Performance Notes

- **First Start**: ~5-10 minutes (Ollama downloads 1.87 GiB model)
- **Chat Response**: ~55 seconds (normal for CPU inference on Llama 3.2 3B)
- **Memory**: ~4-6 GB recommended
- **CPU**: Multi-core processor improves performance

## Cleanup

```bash
# Stop and remove container
docker-compose -f docker-compose.allinone.yml down

# Remove image
docker rmi ethics-allinone

# Remove all (container + image + volumes)
docker-compose -f docker-compose.allinone.yml down -v
```

## Deployment to Azure

### 1. Build and Push to Registry

```bash
# Login to Azure Registry
az acr login --name ethicsacr

# Build
docker build -t ethicsacr.azurecr.io/rag-allinone:latest -f Dockerfile.allinone .

# Push
docker push ethicsacr.azurecr.io/rag-allinone:latest
```

### 2. Deploy to Azure Container Instances

```bash
az container create \
  --resource-group ethics-rg \
  --name rag-app \
  --image ethicsacr.azurecr.io/rag-allinone:latest \
  --cpu 2 --memory 4 \
  --ports 3000 \
  --environment-variables \
    PYTHONPATH=src \
    CHROMA_DIR=/app/Vectorestor \
    REQUEST_TIMEOUT=600 \
    OLLAMA_REQUEST_TIMEOUT=600
```

### 3. Verify Deployment

```bash
# Get container IP
az container show \
  --resource-group ethics-rg \
  --name rag-app \
  --query ipAddress.ip -o tsv

# Access
http://<container-ip>:3000/
```

## Key Advantages

✅ **Single Container** - Simpler deployment and management  
✅ **All Services Included** - No external dependencies  
✅ **600s Timeouts** - Handles long-running LLM requests  
✅ **Streaming Support** - Nginx properly configured  
✅ **Auto-Restart** - Supervisor keeps services running  
✅ **Health Checks** - Docker monitors container health  
✅ **Easy Scaling** - Can run multiple instances  

This is the **recommended approach** for both local development and Azure production!
  -v $(pwd)/Vectorestor:/app/Vectorestor \
  ethics-allinone
```

### Or with docker-compose:
```bash
docker-compose -f docker-compose.allinone.yml up --build
```

### Test:
```bash
# Frontend
curl http://localhost:3000

# Backend
curl http://localhost:8000/docs

# Ollama
curl http://localhost:11434/api/tags
```

---

## Deploy to Azure App Service

### Step 1: Build and push to ACR

```bash
# Build
docker build -t ethicsacr.azurecr.io/ethics-allinone:latest -f Dockerfile.allinone .

# Login to ACR
az acr login --name ethicsacr

# Push
docker push ethicsacr.azurecr.io/ethics-allinone:latest
```

### Step 2: Update App Service

1. Go to **Azure Portal** → **ethics-plan**
2. Go to **Deployment Center**
3. Set image:
   - Registry: `ethicsacr`
   - Image: `ethics-allinone`
   - Tag: `latest`
4. Click **Save**

### Step 3: Configure App Service

1. Go to **Configuration** (App settings)
2. Update environment variables:
   ```
   PORT=3000
   PYTHONPATH=src
   CHROMA_DIR=/app/Vectorestor
   OLLAMA_LLM_ENDPOINT=http://localhost:11434/
   OLLAMA_EMBEDDINGS_ENDPOINT=http://localhost:11434/
   REACT_APP_BASE_URL=http://localhost:8000/
   ```

3. Or for external access:
   ```
   REACT_APP_BASE_URL=https://ethics-plan-cub9e5byh5b5gjbs.switzerlandnorth-01.azurewebsites.net/
   ```

4. Click **Save**

### Step 4: Wait for deployment

- Container pulls from ACR
- Supervisor starts all services
- ~2-3 minutes to start
- Ollama models auto-download on first run

---

## What Happens Inside the Container

### On startup:
1. **Ollama starts** → Downloads models (llama3.2, nomic-embed-text)
2. **FastAPI starts** → Connects to Ollama and Chroma
3. **Nginx starts** → Serves React frontend

### Port mapping:
- **3000** → Nginx (React app)
- **8000** → FastAPI (Backend API)
- **11434** → Ollama (LLM service)

### Frontend talks to backend via:
```javascript
REACT_APP_BASE_URL = http://localhost:8000/
```

---

## Monitoring

### View logs:
```bash
# Azure Portal
Portal → ethics-plan → Log Stream

# Or via Azure CLI
az webapp log tail -g ethics-rg --name ethics-plan
```

### Expected log output:
```
Supervisor started with PID 1
Spawning nginx with PID xxx
Spawning fastapi with PID xxx
Spawning ollama with PID xxx
Ollama serving on 0.0.0.0:11434
Uvicorn running on 0.0.0.0:8000
Nginx started
```

### Check service status:
```bash
# SSH into container (from Portal)
# Then check supervisor status

supervisorctl status
# Should show:
# fastapi    RUNNING
# nginx      RUNNING
# ollama     RUNNING
```

---

## Advantages of All-in-One

✅ **Simple** - One container, one image  
✅ **No networking issues** - All services on localhost  
✅ **Easy debugging** - All logs in one place  
✅ **Perfect for demos** - Full stack works immediately  
✅ **Azure App Service compatible** - Works with existing setup  

---

## Disadvantages

❌ **Larger container** - ~2GB (includes Python, Node, Ollama)  
❌ **Slower startup** - Ollama model download takes time  
❌ **Can't scale services independently** - All scale together  
❌ **Resource intensive** - Needs 2GB RAM minimum  

---

## Troubleshooting

### Container won't start
```bash
# Check logs
az webapp log tail -g ethics-rg --name ethics-plan

# Common issues:
# - PORT already in use
# - Ollama models failing to download
# - FastAPI import errors
```

### Nginx not serving frontend
```bash
# SSH into container
# Check nginx config
cat /etc/nginx/conf.d/frontend.conf.template

# Restart nginx
supervisorctl restart nginx
```

### Backend not responding
```bash
# SSH into container
# Check FastAPI logs
tail -f /var/log/supervisor/fastapi.out.log

# Restart backend
supervisorctl restart fastapi
```

### Ollama not running
```bash
# SSH into container
# Check Ollama logs
tail -f /var/log/supervisor/ollama.out.log

# Restart Ollama
supervisorctl restart ollama
```

---

## Next Steps

1. **Test locally first:**
   ```bash
   docker build -t ethics-allinone -f Dockerfile.allinone .
   docker run -p 3000:3000 -p 8000:8000 -p 11434:11434 ethics-allinone
   ```

2. **Build and push to ACR:**
   ```bash
   docker push ethicsacr.azurecr.io/ethics-allinone:latest
   ```

3. **Update App Service:**
   - Deployment Center → Select ethics-allinone:latest
   - Save and wait for deployment

4. **Test the app:**
   - Frontend: https://ethics-plan-cub9e5byh5b5gjbs.switzerlandnorth-01.azurewebsites.net/
   - API: https://ethics-plan-cub9e5byh5b5gjbs.switzerlandnorth-01.azurewebsites.net:8000/docs

---

## Performance Tips

### Reduce startup time:
- Pre-download Ollama models in Dockerfile
- Use layer caching effectively

### Reduce container size:
- Use slim base images
- Remove build dependencies

### Optimize memory:
- Monitor with: `docker stats`
- Adjust Ollama model size if needed

---

## Alternative: GitHub Actions Automation

Create a workflow to automatically:
1. Build Dockerfile.allinone
2. Push to ACR
3. Trigger App Service deployment

Want me to set this up? 🚀

---

## Quick Reference

| Component | Port | Service |
|-----------|------|---------|
| Frontend | 3000 | Nginx |
| Backend API | 8000 | FastAPI |
| LLM Service | 11434 | Ollama |
| Supervisor UI | - | Internal only |

---

**Status:** All-in-one setup ready for deployment  
**Next:** Choose local test or direct to Azure
