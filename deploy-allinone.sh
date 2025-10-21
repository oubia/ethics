#!/bin/bash
# Deploy all-in-one container to Azure ACR and App Service

set -e

# Configuration
ACR_NAME="ethicsacr"
ACR_URL="${ACR_NAME}.azurecr.io"
IMAGE_NAME="ethics-allinone"
IMAGE_TAG="latest"
RESOURCE_GROUP="ethics-rg"
APP_NAME="ethics-plan"

echo "=========================================="
echo "Building & Deploying All-in-One Container"
echo "=========================================="

# Step 1: Build image
echo ""
echo "📦 Step 1: Building Docker image..."
docker build -t ${ACR_URL}/${IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile.allinone .

# Step 2: Login to ACR
echo ""
echo "🔐 Step 2: Logging into Azure Container Registry..."
az acr login --name ${ACR_NAME}

# Step 3: Push to ACR
echo ""
echo "📤 Step 3: Pushing image to ACR..."
docker push ${ACR_URL}/${IMAGE_NAME}:${IMAGE_TAG}

echo ""
echo "✅ Image pushed successfully!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Go to Azure Portal: https://portal.azure.com"
echo "2. Navigate to: Resource groups → ${RESOURCE_GROUP} → ${APP_NAME}"
echo "3. Go to: Settings → Deployment Center"
echo "4. Set image:"
echo "   - Registry: ${ACR_NAME}"
echo "   - Image: ${IMAGE_NAME}"
echo "   - Tag: ${IMAGE_TAG}"
echo "5. Click 'Save'"
echo "6. Wait 3-5 minutes for deployment"
echo ""
echo "✨ Your app will be available at:"
echo "   Frontend: https://${APP_NAME}-*.azurewebsites.net/"
echo "   Backend:  https://${APP_NAME}-*.azurewebsites.net:8000/docs"
echo ""
