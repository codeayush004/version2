#!/bin/bash

# Configuration
RESOURCE_GROUP="rg-container-optimizer"
LOCATION="southeastasia"
ACR_NAME="acroptimizer$(date +%s)"
APP_PLAN_NAME="plan-optimizer"
WEB_APP_NAME="app-optimizer-v11-$(date +%s)"

echo "Starting Azure Deployment for Southeast Asia ($LOCATION)..."

# 1. Create Resource Group
echo "Creating Resource Group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Azure Container Registry
echo "Creating ACR: $ACR_NAME..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# 3. Create App Service Plan (Linux)
echo "Creating App Service Plan..."
az appservice plan create --name $APP_PLAN_NAME --resource-group $RESOURCE_GROUP --is-linux --sku B1 --location $LOCATION

# 4. Build and Push Backend Image (Manual step usually, but providing command)
echo "NOTE: You must login to ACR and push your images first."
echo "az acr login --name $ACR_NAME"
# docker build -t $ACR_NAME.azurecr.io/backend:latest ./backend
# docker push $ACR_NAME.azurecr.io/backend:latest

# 5. Create Web App for Containers (Backend)
echo "Creating Web App: $WEB_APP_NAME..."
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_PLAN_NAME --name $WEB_APP_NAME --deployment-container-image-name "$ACR_NAME.azurecr.io/backend:latest"

echo "Azure Resources Initialized in $LOCATION!"
echo "Web App URL: https://$WEB_APP_NAME.azurewebsites.net"
