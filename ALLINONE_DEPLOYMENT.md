# All-in-One Deployment Guide

This deployment uses a single container running all services (Frontend, Backend, Ollama) together with proper timeout configurations for long-running LLM requests.

## Overview

All services run in **one Docker container**:
- ✅ Frontend (React + Nginx on port 3000)
- ✅ Backend (FastAPI on port 8000) - internal communication
- ✅ Ollama (on port 11434) - internal communication
- ✅ Supervisor - Process manager for all services
- ✅ 600s timeouts configured for all proxy/API calls

## Architecture

```
Single Docker Container (ethics-app)
├── Supervisor (Process Manager)
│   ├── Nginx (port 3000)
│   │   ├── Serves React frontend (static files)
│   │   └── Proxies /chat/, /process_audio/, /api/ to Backend
│   ├── FastAPI (port 8000)
│   │   └── Processes API requests
│   └── Ollama (port 11434)
│       └── Runs LLM inference
│
└── All timeouts: 600s (10 minutes) for long-running requests
```

## Ports Overview

- **3000** - Public frontend access (Nginx serving React + API proxy)
- **8000** - Backend API (internal only, accessible for debugging)
- **11434** - Ollama LLM server (internal only, accessible for direct API calls)

## Build and Run

### Using docker-compose (Recommended)

```bash
# Build
docker-compose -f docker-compose.allinone.yml build

# Start
docker-compose -f docker-compose.allinone.yml up -d

# Check status
docker-compose -f docker-compose.allinone.yml ps

# View logs
docker-compose -f docker-compose.allinone.yml logs -f app

# Stop
docker-compose -f docker-compose.allinone.yml down
```

### Direct Docker Build and Run

```bash
# Build the image
docker build -t ethics-allinone -f Dockerfile.allinone .

# Run with all ports exposed
docker run -d \
  --name ethics-app \
  -p 3000:3000 \
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
