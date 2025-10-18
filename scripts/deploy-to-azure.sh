#!/usr/bin/env bash
# Deploy to Azure Container Instances using docker-compose
# This script builds and pushes images to ACR, then deploys to ACI

set -euo pipefail

# Configuration from environment or defaults
ACR_LOGIN_SERVER="${AZURE_REGISTRY_LOGIN_SERVER}"
ACR_USERNAME="${AZURE_REGISTRY_USERNAME}"
ACR_PASSWORD="${AZURE_REGISTRY_PASSWORD}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-ethics-rg}"
CONTAINER_GROUP_NAME="${CONTAINER_GROUP_NAME:-ethics-app}"

if [ -z "$ACR_LOGIN_SERVER" ] || [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
  echo "Error: Azure Container Registry credentials not set." >&2
  echo "Set: AZURE_REGISTRY_LOGIN_SERVER, AZURE_REGISTRY_USERNAME, AZURE_REGISTRY_PASSWORD" >&2
  exit 1
fi

echo "Logging into Azure Container Registry: $ACR_LOGIN_SERVER"
echo "$ACR_PASSWORD" | docker login -u "$ACR_USERNAME" --password-stdin "$ACR_LOGIN_SERVER"

echo "Building and pushing backend image..."
docker build -t "$ACR_LOGIN_SERVER/ethics-backend:latest" ./backend
docker push "$ACR_LOGIN_SERVER/ethics-backend:latest"

echo "Building and pushing frontend image..."
docker build \
  --build-arg REACT_APP_BASE_URL="${REACT_APP_BASE_URL:-https://api.ethics.oubia.me/}" \
  -t "$ACR_LOGIN_SERVER/ethics-frontend:latest" ./frontend
docker push "$ACR_LOGIN_SERVER/ethics-frontend:latest"

echo "Building and pushing Ollama image..."
docker build -t "$ACR_LOGIN_SERVER/ethics-ollama:latest" ./Ollama
docker push "$ACR_LOGIN_SERVER/ethics-ollama:latest"

echo "Images pushed successfully!"
echo "Now deploy using Azure Portal or Azure CLI:"
echo ""
echo "az container create \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --name $CONTAINER_GROUP_NAME \\"
echo "  --image $ACR_LOGIN_SERVER/ethics-frontend:latest \\"
echo "  --registry-login-server $ACR_LOGIN_SERVER \\"
echo "  --registry-username $ACR_USERNAME \\"
echo "  --registry-password '***' \\"
echo "  --cpu 2 --memory 2 \\"
echo "  --ports 80 443 \\"
echo "  --environment-variables CADDY_DOMAIN='ethics.oubia.me' \\"
echo "  --restart-policy OnFailure"
