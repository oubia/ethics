# Quick Deployment Commands

## Build and Push All-in-One to Azure

### Option 1: Use the deployment script (Recommended)
```bash
cd /Users/oubia/Desktop/Folder/ethics
chmod +x deploy-allinone.sh
./deploy-allinone.sh
```

### Option 2: Manual commands
```bash
# 1. Build the image
docker build -t ethicsacr.azurecr.io/ethics-allinone:latest -f Dockerfile.allinone .

# 2. Login to ACR
az acr login --name ethicsacr

# 3. Push to ACR
docker push ethicsacr.azurecr.io/ethics-allinone:latest
```

---

## Update Azure App Service

### Via Azure Portal (Easiest)
1. Go to: https://portal.azure.com
2. Search for: **ethics-plan**
3. Go to: **Deployment Center**
4. Fill in:
   - **Registry**: ethicsacr
   - **Image**: ethics-allinone
   - **Tag**: latest
5. Click **Save**
6. Wait 3-5 minutes for deployment

### Via Azure CLI
```bash
# Update app service to use new image
az webapp create \
  --resource-group ethics-rg \
  --plan ethics-plan \
  --name ethics-plan \
  --deployment-container-image-name ethicsacr.azurecr.io/ethics-allinone:latest \
  --docker-registry-server-url https://ethicsacr.azurecr.io \
  --docker-registry-server-user ethicsacr \
  --docker-registry-server-password YOUR_PASSWORD

# Or restart to pull latest image
az webapp restart --resource-group ethics-rg --name ethics-plan
```

---

## Test Deployment

### Once deployed, test these URLs:
```bash
# Frontend (React app)
https://ethics-plan-cub9e5byh5b5gjbs.switzerlandnorth-01.azurewebsites.net/

# Backend API (FastAPI docs)
https://ethics-plan-cub9e5byh5b5gjbs.switzerlandnorth-01.azurewebsites.net:8000/docs

# Ollama health
https://ethics-plan-cub9e5byh5b5gjbs.switzerlandnorth-01.azurewebsites.net:11434/api/tags
```

---

## Monitor Logs

### In Azure Portal:
1. Go to: **ethics-plan**
2. Go to: **Log Stream** (real-time logs)
3. Or: **Monitoring** → **Logs** → **Kudu** for detailed logs

### Via Azure CLI:
```bash
az webapp log tail --resource-group ethics-rg --name ethics-plan
```

### Expected output:
```
[supervisord] started with PID 1
spawned: 'nginx' with pid 10
spawned: 'fastapi' with pid 11
spawned: 'ollama' with pid 12
entered RUNNING state
2025/10/21 nginx started
Uvicorn running on 0.0.0.0:8000
Ollama serving
```

---

## Troubleshooting

### Container won't start?
1. Check logs in Azure Portal → Log Stream
2. Common issues:
   - Image not found in ACR → Verify image was pushed
   - Port already in use → Check PORT env var (should be 3000)
   - Dependencies missing → Check requirements.txt

### Backend not responding?
```bash
# SSH into container
az webapp ssh --resource-group ethics-rg --name ethics-plan

# Check supervisor status
supervisorctl status
# Should show:
# fastapi    RUNNING
# nginx      RUNNING
# ollama     RUNNING
```

### Nginx showing old frontend?
```bash
# Clear Azure container cache
az webapp deployment source sync --resource-group ethics-rg --name ethics-plan
```

---

## After Deployment Checklist

- [ ] Build Docker image locally (no errors)
- [ ] Image pushed to ACR ethicsacr.azurecr.io/ethics-allinone:latest
- [ ] App Service deployment center updated
- [ ] App Service restarted/redeployed
- [ ] Check logs - no startup errors
- [ ] Frontend loads at https://ethics-plan-...azurewebsites.net/
- [ ] API responds at :8000/docs
- [ ] Chat feature works (connects frontend to backend)
- [ ] Models downloading (first Ollama call will auto-download)

---

## Remember

**Total deployment time:**
- Build: ~3-5 minutes
- Push to ACR: ~2-3 minutes
- Deploy to App Service: ~3-5 minutes
- First run (model download): ~10-20 minutes
- **Total: ~20-30 minutes on first run**

Subsequent deployments will be faster since models are cached!

---

## Need Help?

Check the full guide: `ALLINONE_DEPLOYMENT.md`
