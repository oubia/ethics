# All-in-One Deployment Quick Start (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ethics AI - All-in-One Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Navigate to project
Write-Host "Step 1: Navigating to project directory..." -ForegroundColor Yellow
Set-Location "d:\homy\Boss fight\Ethics\ethics"
Write-Host "✓ In project directory" -ForegroundColor Green
Write-Host ""

# Step 2: Build image
Write-Host "Step 2: Building Docker image (this takes 2-3 minutes)..." -ForegroundColor Yellow
docker build -f Dockerfile.allinone -t ethics-allinone:latest . | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Image built successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Stop any existing containers
Write-Host "Step 3: Stopping previous containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.allinone.yml down -v 2>$null
Write-Host "✓ Previous containers cleaned" -ForegroundColor Green
Write-Host ""

# Step 4: Start containers
Write-Host "Step 4: Starting containers with docker-compose..." -ForegroundColor Yellow
docker-compose -f docker-compose.allinone.yml up -d | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Containers started" -ForegroundColor Green
Write-Host ""

# Step 5: Wait for services
Write-Host "Step 5: Waiting for Ollama to load model (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60
Write-Host "✓ Services should be ready" -ForegroundColor Green
Write-Host ""

# Step 6: Verify containers
Write-Host "Step 6: Verifying all services are running..." -ForegroundColor Yellow
docker-compose -f docker-compose.allinone.yml ps
Write-Host ""

# Step 7: Test endpoints
Write-Host "Step 7: Testing endpoints..." -ForegroundColor Yellow
Write-Host ""

# Test frontend
Write-Host -NoNewLine "  Testing frontend... "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/" -TimeoutSec 5 -ErrorAction Stop
    if ($response.Content -like "*React*" -or $response.Content -like "*html*") {
        Write-Host "✓" -ForegroundColor Green
    } else {
        Write-Host "⚠ (responded but no React)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗" -ForegroundColor Red
}

# Test health endpoint
Write-Host -NoNewLine "  Testing health endpoint... "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.Content -like "*ok*") {
        Write-Host "✓" -ForegroundColor Green
    } else {
        Write-Host "✗" -ForegroundColor Red
    }
} catch {
    Write-Host "✗" -ForegroundColor Red
}

# Test backend directly
Write-Host -NoNewLine "  Testing backend (8000)... "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.Content -like "*ok*") {
        Write-Host "✓" -ForegroundColor Green
    } else {
        Write-Host "✗" -ForegroundColor Red
    }
} catch {
    Write-Host "✗" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "All-in-One Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000/" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000/" -ForegroundColor White
Write-Host "  Ollama:    http://localhost:11434/" -ForegroundColor White
Write-Host ""

Write-Host "Quick Commands:" -ForegroundColor Cyan
Write-Host "  View logs:     docker logs ethics-app -f" -ForegroundColor White
Write-Host "  Check status:  docker-compose -f docker-compose.allinone.yml ps" -ForegroundColor White
Write-Host "  Stop:          docker-compose -f docker-compose.allinone.yml down" -ForegroundColor White
Write-Host ""

Write-Host "Test Long Request (55+ seconds, should NOT timeout):" -ForegroundColor Cyan
Write-Host @'
$body = @{message="Explain AI ethics in 5 points"} | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://localhost:3000/chat/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body `
  -TimeoutSec 600
Write-Host "Response received! No timeout at 60 seconds."
'@ -ForegroundColor White
Write-Host ""

Write-Host "Push to Azure Registry:" -ForegroundColor Cyan
Write-Host "  docker push ethicsacr.azurecr.io/ethics-allinone:latest" -ForegroundColor White
Write-Host ""

Write-Host "See ALLINONE_DEPLOYMENT.md for Azure deployment steps" -ForegroundColor Yellow
