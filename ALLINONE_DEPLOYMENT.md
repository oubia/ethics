# All-in-One Container Deployment Guide

## Overview

Instead of deploying separate services, everything runs in **one Docker container**:
- ✅ Frontend (React + Nginx on port 3000)
- ✅ Backend (FastAPI on port 8000)
- ✅ Ollama (on port 11434)
- All managed by Supervisor

This is **simpler** and **works great for Azure App Service**.

---

## Architecture

```
┌─────────────────────────────────────────┐
│     Single Docker Container             │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │  Supervisor (Process Manager)   │    │
│  └─────────────────────────────────┘    │
│    ├── Nginx (port 3000)                │
│    │   └── React app (static files)     │
│    ├── FastAPI (port 8000)              │
│    │   └── Backend API                  │
│    └── Ollama (port 11434)              │
│        └── LLM models                   │
└─────────────────────────────────────────┘
```

---

## Files Created

1. **`Dockerfile.allinone`** - All-in-one container image
2. **`docker-compose.allinone.yml`** - Compose file for local testing

---

## Local Testing (Before Azure)

### Build the image:
```bash
docker build -t ethics-allinone -f Dockerfile.allinone .
```

### Run locally:
```bash
docker run -p 3000:3000 -p 8000:8000 -p 11434:11434 \
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
