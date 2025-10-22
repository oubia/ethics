#!/bin/bash
# All-in-One Deployment Quick Start Script

echo "=========================================="
echo "Ethics AI - All-in-One Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Navigate to project
echo -e "${YELLOW}Step 1: Navigating to project directory...${NC}"
cd "d:\homy\Boss fight\Ethics\ethics" || exit 1
echo -e "${GREEN}✓ In project directory${NC}"
echo ""

# Step 2: Build image
echo -e "${YELLOW}Step 2: Building Docker image (this takes 2-3 minutes)...${NC}"
docker build -f Dockerfile.allinone -t ethics-allinone:latest . || {
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Image built successfully${NC}"
echo ""

# Step 3: Start containers
echo -e "${YELLOW}Step 3: Starting containers with docker-compose...${NC}"
docker-compose -f docker-compose.allinone.yml down -v 2>/dev/null
docker-compose -f docker-compose.allinone.yml up -d || {
    echo -e "${RED}✗ Failed to start containers${NC}"
    exit 1
}
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Step 4: Wait for services
echo -e "${YELLOW}Step 4: Waiting for services to start (60 seconds)...${NC}"
sleep 60
echo -e "${GREEN}✓ Services should be ready${NC}"
echo ""

# Step 5: Verify containers
echo -e "${YELLOW}Step 5: Verifying all services are running...${NC}"
docker-compose -f docker-compose.allinone.yml ps
echo ""

# Step 6: Test endpoints
echo -e "${YELLOW}Step 6: Testing endpoints...${NC}"

# Test frontend
echo -n "Testing frontend... "
if curl -s http://localhost:3000/ | grep -q "React"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test health
echo -n "Testing health endpoint... "
if curl -s http://localhost:3000/health | grep -q "ok"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test backend directly
echo -n "Testing backend... "
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All-in-One Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000/"
echo "Backend API: http://localhost:8000/health"
echo "Ollama: http://localhost:11434/"
echo ""
echo "Next steps:"
echo "1. Open browser: http://localhost:3000/"
echo "2. Test chat (takes 55+ seconds)"
echo "3. Check logs: docker logs ethics-app -f"
echo "4. Stop: docker-compose -f docker-compose.allinone.yml down"
echo ""
echo "Ready to push to Azure:"
echo "  docker push ethicsacr.azurecr.io/ethics-allinone:latest"
echo ""
