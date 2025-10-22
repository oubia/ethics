# Command Reference - Quick Deploy & Test

## 📦 Deployment Commands

```bash
# Navigate to project
cd "d:\homy\Boss fight\Ethics\ethics"

# Option 1: Full rebuild (recommended)
docker-compose down
docker-compose build
docker-compose up -d

# Option 2: Just restart (if already built)
docker-compose up -d

# Option 3: Rebuild specific service
docker-compose build nginx
docker-compose up -d nginx
```

## 🔍 Verification Commands

```bash
# Check all services running
docker-compose ps

# Check service health
docker-compose ps | findstr "healthy"

# View container logs
docker-compose logs -f

# View specific container
docker-compose logs -f rag-backend
docker-compose logs -f rag-nginx
docker-compose logs -f ollama

# View last N lines
docker-compose logs --tail 50 rag-backend
```

## 🧪 Testing Commands

```bash
# Health check endpoint
curl http://localhost:8080/health

# Health check backend
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8080/chat/ ^
  -H "Content-Type: application/json" ^
  -d "{\"content\":\"What is AI?\",\"selectedapproach\":\"default\",\"selectedChunkSize\":512,\"selectedapproachRetriever\":\"default\"}"

# Test with verbose output
curl -v http://localhost:8080/health
```

## 🔧 Debugging Commands

```bash
# Check if ports are available
netstat -an | findstr ":8080"
netstat -an | findstr ":8000"
netstat -an | findstr ":11434"

# Check nginx configuration syntax
docker-compose exec nginx nginx -t

# Check container resource usage
docker stats

# Inspect service network
docker network inspect ethics_rag-network

# Check environment variables in container
docker-compose exec backend env | grep TIMEOUT

# Test backend connectivity from nginx
docker-compose exec nginx curl http://backend:8000/health

# Test ollama from backend
docker-compose exec backend curl http://ollama:11434/api/tags
```

## 📊 Monitoring Commands

```bash
# Real-time logs with timestamps
docker-compose logs -f --timestamps

# Follow specific container
docker-compose logs -f rag-backend --tail 100

# Show only errors
docker-compose logs rag-backend | findstr "ERROR"

# Show full container output
docker logs rag-backend -f

# Get container ID
docker-compose ps -q rag-backend
```

## 🧹 Cleanup Commands

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove all stopped containers
docker container prune -f

# Remove dangling images
docker image prune -f

# Full cleanup (use with caution!)
docker-compose down -v
docker system prune -f
```

## 🐛 Troubleshooting Commands

```bash
# Restart a service
docker-compose restart rag-backend

# Restart all services
docker-compose restart

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Check if service is accessible
docker-compose exec backend ping ollama

# Copy file from container
docker cp rag-backend:/app/config.json ./

# Copy file to container
docker cp ./nginx.conf rag-nginx:/etc/nginx/nginx.conf

# Restart nginx after config change
docker-compose exec nginx nginx -s reload
```

## 📈 Performance Commands

```bash
# Watch resource usage
docker stats --no-stream

# Get container details
docker inspect rag-backend

# Check image sizes
docker images | findstr "rag-"

# See network bridges
docker network ls

# Inspect network details
docker network inspect ethics_rag-network
```

## 🔑 Important Timeouts Configured

```bash
# Check settings in container
docker-compose exec backend grep -r "TIMEOUT" src/config/

# View environment variables
docker-compose config | grep -i "timeout"

# Print active settings
docker-compose exec backend python -c "from src.config.settings import *; print(f'OLLAMA_REQUEST_TIMEOUT: {OLLAMA_REQUEST_TIMEOUT}')"
```

## 📝 File Verification

```bash
# Check nginx config is correct
Find-Content "d:\homy\Boss fight\Ethics\ethics\nginx.conf" -Pattern "proxy_read_timeout"

# Check docker-compose has nginx
Select-String "d:\homy\Boss fight\Ethics\ethics\docker-compose.yml" -Pattern "nginx:"

# Check settings has timeouts
Select-String "d:\homy\Boss fight\Ethics\ethics\backend\src\config\settings.py" -Pattern "TIMEOUT"

# Check main.py has health endpoint
Select-String "d:\homy\Boss fight\Ethics\ethics\backend\main.py" -Pattern "@app.get"
```

## 🚀 Full Deployment Workflow

```bash
# 1. Navigate
cd "d:\homy\Boss fight\Ethics\ethics"

# 2. Stop old containers
docker-compose down

# 3. Build
docker-compose build

# 4. Start
docker-compose up -d

# 5. Wait for health
timeout /t 30
docker-compose ps

# 6. Test health
curl http://localhost:8080/health

# 7. Monitor
docker-compose logs -f

# 8. Test chat (wait 60+ seconds)
curl -X POST http://localhost:8080/chat/ ...
```

## 🎯 One-Liner Commands

```bash
# Full reset and deploy
docker-compose down && docker-compose build && docker-compose up -d && docker-compose ps

# Check all health
docker-compose ps | findstr healthy

# Test all endpoints
curl http://localhost:8080/health && echo "" && curl http://localhost:8000/health

# Monitor all logs
docker-compose logs -f

# Kill all Docker
docker-compose down -v && docker system prune -f
```

## 📱 WSL/PowerShell Specific

```bash
# PowerShell - Full deployment
$ErrorActionPreference = "Stop"
cd "d:\homy\Boss fight\Ethics\ethics"
docker-compose down
docker-compose build
docker-compose up -d
docker-compose ps

# PowerShell - Wait and test
Start-Sleep -Seconds 10
Invoke-WebRequest -Uri "http://localhost:8080/health" -Method Get

# PowerShell - Real-time monitoring
while ($true) { docker-compose ps; Start-Sleep -Seconds 5; Clear-Host }
```

---

## Reference: Port Mapping

| Service | Port | Type | Access |
|---------|------|------|--------|
| Nginx | 8080 | Public | ✅ http://localhost:8080 |
| Backend | 8000 | Internal | ⚠️ Only from nginx |
| Ollama | 11434 | Internal | ⚠️ Only from backend |
| Frontend | 3000 | Development | Optional for local dev |

---

## 📞 Common Issues & Fixes

```bash
# Port already in use
# Solution: Stop docker or change port in docker-compose.yml

# Connection refused
docker-compose restart nginx

# Timeout still happening
# Check: docker-compose config | grep -i timeout

# Service not healthy
docker-compose logs rag-backend

# Can't connect to ollama
docker-compose exec backend curl http://ollama:11434/api/tags

# Nginx config error
docker-compose exec nginx nginx -t
```
