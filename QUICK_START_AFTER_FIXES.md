# Quick Start Guide - After Fixes

## What Was Fixed

✅ Nginx PORT configuration issue  
✅ Missing Whisper audio model  
✅ Missing FFmpeg  
✅ Frontend Docker incomplete  
✅ Docker compose indentation  

---

## Pre-Flight Checklist

### 1. Create Environment File
```bash
# Copy the example file
cp .env.example .env

# Edit for your environment
nano .env
```

**For development**, keep default:
```
REACT_APP_BASE_URL="http://127.0.0.1:8000/"
```

**For production**, update to:
```
REACT_APP_BASE_URL="https://api.ethics.oubia.me/"
```

### 2. Ensure Vectorestor Directory
```bash
# Create if it doesn't exist
mkdir -p ./Vectorestor
chmod 755 ./Vectorestor
```

### 3. Verify Docker Resources
```bash
# Check Docker has enough space (need ~10GB)
docker system df
docker system prune -a  # Clean up if needed
```

---

## Development Deployment

### Start Everything
```bash
# Build and start all services
docker-compose up --build

# Watch logs
docker-compose logs -f
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434/api/tags

### First Run
- ⏳ Ollama will download models (~5-10 minutes)
- ⏳ Whisper will cache models on first audio upload
- ✅ Everything should work after initial setup

---

## Production Deployment

### Before Deployment

1. **DNS Configuration**
   ```
   ethics.oubia.me → Your Server IP
   api.ethics.oubia.me → Your Server IP
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   nano .env
   ```

3. **Ensure Space**
   ```bash
   df -h  # Need 15GB+ free space
   ```

### Deploy
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d --build

# Monitor
docker-compose -f docker-compose.prod.yml logs -f
```

### Access Points
- **Frontend**: https://ethics.oubia.me
- **Backend API**: https://api.ethics.oubia.me
- **API Docs**: https://api.ethics.oubia.me/docs

---

## Health Checks

### All Services Running?
```bash
docker-compose ps
# All should show "Up"
```

### Backend Healthy?
```bash
curl -s http://localhost:8000/docs | head -20
# Should return HTML
```

### Ollama Ready?
```bash
curl -s http://localhost:11434/api/tags | jq '.models | length'
# Should return 2 (after models downloaded)
```

### Frontend Serving?
```bash
curl -s http://localhost:3000 | head -10
# Should return HTML
```

---

## Common Issues & Solutions

### Issue: "invalid port in ${PORT:-80}"
**Status**: ✅ FIXED  
Already corrected in `Dockerfile.prod`

### Issue: Audio endpoint not working
**Status**: ✅ FIXED  
- FFmpeg installed in backend
- Whisper module added to requirements

### Issue: Frontend not loading
**Status**: ✅ FIXED  
- Added nginx runner stage to frontend Dockerfile
- React app now properly served

### Issue: Services won't start
```bash
# Check logs
docker-compose logs

# Clean and retry
docker-compose down -v
docker-compose up --build
```

### Issue: Port already in use
```bash
# Change ports in docker-compose.yml or
lsof -i :3000  # Find what's using port
kill -9 <PID>
```

---

## Useful Commands

```bash
# View running services
docker-compose ps

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs ollama

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Remove volumes (CAREFUL - deletes data)
docker-compose down -v

# Rebuild specific service
docker-compose up --build backend

# Execute command in running container
docker-compose exec backend python -c "import whisper; print('OK')"

# View docker resource usage
docker stats
```

---

## Performance Optimization

### Increase Docker Resources
```bash
# Edit Docker Desktop settings or for Linux:
# Make sure /etc/docker/daemon.json has:
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
```

### Monitor Usage
```bash
# Watch resource consumption
watch 'docker stats --no-stream'

# Check disk usage
docker system df -v
```

---

## Troubleshooting Checklist

- [ ] `.env` file exists and is readable
- [ ] `./Vectorestor` directory exists with proper permissions
- [ ] Docker daemon is running
- [ ] Ports 3000, 8000, 11434 are available (dev) or 80/443 (prod)
- [ ] At least 15GB free disk space
- [ ] Docker has network access to pull images/models
- [ ] All services show "Up" in `docker-compose ps`

---

## Getting Help

Check logs for errors:
```bash
# All logs
docker-compose logs

# Specific service with tail
docker-compose logs -f backend

# Show only errors
docker-compose logs backend 2>&1 | grep -i error
```

---

**Status**: All critical fixes applied ✅  
**Ready for deployment**: Yes  
**Estimated first run time**: 10-15 minutes
