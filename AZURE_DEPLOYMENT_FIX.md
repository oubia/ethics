# Azure App Service Deployment Fix

## Issue: Nginx starting on Azure instead of app

The logs show nginx is running, but the frontend container is starting nginx (port 8080) instead of being properly configured for Azure App Service.

## Solution: Use Docker Compose for Azure

### 1. Test Locally First

```bash
# Use azure-specific docker-compose file
docker-compose -f docker-compose.azure.yml down
docker-compose -f docker-compose.azure.yml build
docker-compose -f docker-compose.azure.yml up -d

# Verify
docker-compose -f docker-compose.azure.yml ps

# Test on port 80 (not 8080)
curl http://localhost/health
```

### 2. Key Azure Settings

**docker-compose.azure.yml:**
- Frontend: Port 80 (Azure default) instead of 8080
- Backend: Port 8000 (internal, not exposed to public)
- All services configured for 600s timeouts

**frontend/Dockerfile.azure:**
- Builds React app
- Serves with nginx on PORT=8080 internally
- Nginx proxies /chat/ and /process_audio/ to backend:8000
- All timeouts set to 600s (10 minutes)

### 3. Build and Push to Azure Registry

```bash
# Login
az acr login --name ethicsacr

# Build images
docker build -f frontend/Dockerfile.azure -t ethicsacr.azurecr.io/rag-frontend:latest ./frontend
docker build -t ethicsacr.azurecr.io/rag-backend:latest ./backend
docker build -t ethicsacr.azurecr.io/ollama:latest ./Ollama

# Push to registry
docker push ethicsacr.azurecr.io/rag-frontend:latest
docker push ethicsacr.azurecr.io/rag-backend:latest
docker push ethicsacr.azurecr.io/ollama:latest
```

### 4. Deploy to Azure Container Instances

```bash
# Create container group from docker-compose
az container create \
  --resource-group ethics-rg \
  --name rag-app \
  --file docker-compose.azure.yml \
  --registry-login-server ethicsacr.azurecr.io \
  --registry-username ethicsacr \
  --registry-password <your-password>
```

### 5. Access Application

```
Frontend: http://<container-ip>/
Health: http://<container-ip>/health
```

## Files Created

- `docker-compose.azure.yml` - Azure deployment configuration
- `frontend/Dockerfile.azure` - Azure-optimized frontend

## Key Differences from Local Setup

| Setting | Local | Azure |
|---------|-------|-------|
| Frontend Port | 8080 | 80 |
| Deployment | docker-compose up | ACR + ACI/App Service |
| Timeouts | 600s | 600s (same) |
| API Proxy | Frontend nginx | Frontend nginx |

## Next Steps

1. ✅ Test locally with `docker-compose.azure.yml`
2. ✅ Push images to Azure Registry
3. ✅ Deploy to Azure Container Instances
4. ✅ Verify health endpoints
5. ✅ Test long-running chat requests (55+ seconds)

All timeout fixes are included in the Azure deployment!
