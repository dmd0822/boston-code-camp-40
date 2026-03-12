# Travel Agent Application - Azure Infrastructure

This directory contains the Infrastructure as Code (IaC) for deploying the Travel Agent Application to Azure using Bicep and Azure Container Apps.

## Architecture Overview

The deployment creates the following Azure resources:

```
┌─────────────────────────────────────────────────────────────┐
│                     Resource Group                          │
│                                                              │
│  ┌──────────────────┐          ┌────────────────────┐      │
│  │  Azure Container │          │  Azure Container   │      │
│  │    Registry      │──images──│   Apps Environment │      │
│  │   (ACR)          │          │                    │      │
│  └──────────────────┘          │  ┌──────────────┐  │      │
│                                 │  │   Frontend   │  │      │
│  ┌──────────────────┐          │  │ Container App│  │      │
│  │  Azure OpenAI    │          │  └──────┬───────┘  │      │
│  │  (GPT-4o)        │─────────▶│         │          │      │
│  └──────────────────┘          │  ┌──────▼───────┐  │      │
│                                 │  │   Backend    │  │      │
│  ┌──────────────────┐          │  │ Container App│  │      │
│  │  Bing Search API │─────────▶│  └──────────────┘  │      │
│  └──────────────────┘          └────────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **Azure Container Registry (ACR)**: Private Docker registry for application images
2. **Container Apps Environment**: Managed Kubernetes environment for hosting containers
3. **Frontend Container App**: React SPA served via nginx (port 80)
4. **Backend Container App**: FastAPI application on Uvicorn (port 8000)
5. **Azure OpenAI**: GPT-4o model deployment for AI capabilities
6. **Bing Search API**: Web search integration

### Key Features

- **Consumption-based pricing**: Pay only for what you use
- **Auto-scaling**: 0-3 replicas based on HTTP load
- **Managed ingress**: HTTPS endpoints with automatic certificates
- **Secret management**: Secure injection of API keys via Container Apps secrets
- **No authentication/database**: Stateless API for MVP simplicity

## Prerequisites

Before deploying, ensure you have:

1. **Azure CLI** (v2.50.0 or later)
   ```bash
   az --version
   ```
   Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

2. **Bicep CLI** (included with Azure CLI)
   ```bash
   az bicep version
   ```

3. **Docker** (for building images)
   ```bash
   docker --version
   ```
   Install: https://docs.docker.com/get-docker/

4. **Azure Subscription** with permissions to create resources

5. **Azure CLI Login**
   ```bash
   az login
   az account set --subscription <subscription-id>
   ```

## Deployment Guide

### Step 1: Create Resource Group

```bash
# Set variables
$RESOURCE_GROUP = "rg-travel-agent-dev"
$LOCATION = "eastus2"

# Create resource group
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION
```

### Step 2: Deploy Infrastructure

Deploy the Bicep template to create all Azure resources:

```bash
# Deploy with dev parameters
az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file infra/main.bicep `
  --parameters infra/parameters/dev.bicepparam

# Capture outputs
$OUTPUTS = az deployment group show `
  --resource-group $RESOURCE_GROUP `
  --name main `
  --query properties.outputs `
  --output json | ConvertFrom-Json

$ACR_LOGIN_SERVER = $OUTPUTS.acrLoginServer.value
$FRONTEND_URL = $OUTPUTS.frontendUrl.value
$BACKEND_URL = $OUTPUTS.backendUrl.value

Write-Host "ACR Login Server: $ACR_LOGIN_SERVER"
Write-Host "Frontend URL: $FRONTEND_URL"
Write-Host "Backend URL: $BACKEND_URL"
```

**Note**: Initial deployment takes ~10-15 minutes (OpenAI provisioning is the slowest).

### Step 3: Build and Push Docker Images

#### Backend Image

```bash
# Navigate to repo root
cd C:\repos\boston-code-camp-40

# Login to ACR
az acr login --name $ACR_LOGIN_SERVER.Split('.')[0]

# Build and tag backend image
docker build -t "${ACR_LOGIN_SERVER}/travel-agent-backend:0.1.0" .

# Push to ACR
docker push "${ACR_LOGIN_SERVER}/travel-agent-backend:0.1.0"
```

#### Frontend Image

```bash
# Build and tag frontend image
docker build -t "${ACR_LOGIN_SERVER}/travel-agent-frontend:0.1.0" ./frontend

# Push to ACR
docker push "${ACR_LOGIN_SERVER}/travel-agent-frontend:0.1.0"
```

### Step 4: Update Container Apps

After pushing images, the Container Apps will automatically pull and deploy:

```bash
# Check backend status
az containerapp show `
  --resource-group $RESOURCE_GROUP `
  --name travel-agent-dev-backend `
  --query properties.runningStatus

# Check frontend status
az containerapp show `
  --resource-group $RESOURCE_GROUP `
  --name travel-agent-dev-frontend `
  --query properties.runningStatus
```

**If apps don't auto-update**, trigger a revision:

```bash
# Update backend
az containerapp update `
  --resource-group $RESOURCE_GROUP `
  --name travel-agent-dev-backend `
  --image "${ACR_LOGIN_SERVER}/travel-agent-backend:0.1.0"

# Update frontend
az containerapp update `
  --resource-group $RESOURCE_GROUP `
  --name travel-agent-dev-frontend `
  --image "${ACR_LOGIN_SERVER}/travel-agent-frontend:0.1.0"
```

### Step 5: Test the Deployment

```bash
# Test backend health
curl "$BACKEND_URL/health"

# Open frontend in browser
Start-Process $FRONTEND_URL
```

## Environment Variables Reference

### Backend Container App

| Variable | Source | Type | Description |
|----------|--------|------|-------------|
| `AZURE_OPENAI_ENDPOINT` | OpenAI module output | Regular | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | OpenAI module output | Secret | API key for OpenAI |
| `AZURE_OPENAI_DEPLOYMENT` | OpenAI module output | Regular | Model deployment name (gpt-4o) |
| `BING_SEARCH_ENDPOINT` | Bing module output | Regular | Bing Search API endpoint |
| `BING_SEARCH_API_KEY` | Bing module output | Secret | API key for Bing Search |
| `APP_VERSION` | Parameter | Regular | Application version tag |

### Frontend Container App

| Variable | Source | Type | Description |
|----------|--------|------|-------------|
| `BACKEND_URL` | Backend module output | Regular | Backend API URL for proxying |

## Module Reference

### `modules/acr.bicep`
Creates Azure Container Registry with admin user enabled.

**Parameters:**
- `name`: Registry name (alphanumeric only)
- `location`: Azure region
- `skuName`: SKU tier (Basic/Standard/Premium)
- `tags`: Resource tags

**Outputs:**
- `id`, `name`, `loginServer`, `adminUsername`, `adminPassword`

### `modules/container-app-env.bicep`
Creates Container Apps managed environment.

**Parameters:**
- `name`: Environment name
- `location`: Azure region
- `tags`: Resource tags

**Outputs:**
- `id`, `name`

### `modules/container-app.bicep`
Reusable module for deploying container apps.

**Parameters:**
- `name`: App name
- `environmentId`: Container Apps environment ID
- `containerImage`: Docker image with tag
- `targetPort`: Container port (80 or 8000)
- `env`: Environment variable array
- `secrets`: Secrets array
- `registryServer`, `registryUsername`, `registryPassword`: ACR credentials
- `cpu`, `memory`: Resource allocation
- `minReplicas`, `maxReplicas`: Scaling configuration

**Outputs:**
- `id`, `name`, `fqdn`, `url`

### `modules/openai.bicep`
Creates Azure OpenAI resource with GPT-4o deployment.

**Parameters:**
- `name`: OpenAI account name
- `modelName`: AI model (default: gpt-4o)
- `modelVersion`: Model version
- `deploymentName`: Deployment name
- `capacity`: TPM capacity (default: 10)

**Outputs:**
- `id`, `endpoint`, `key`, `deploymentName`

### `modules/bing-search.bicep`
Creates Bing Search API resource (global location).

**Parameters:**
- `name`: Resource name
- `skuName`: SKU tier (S1-S9)

**Outputs:**
- `id`, `endpoint`, `key`

## Cost Estimates (Dev Tier)

Approximate monthly costs for dev environment with minimal usage:

| Resource | SKU/Tier | Estimated Cost |
|----------|----------|----------------|
| Azure Container Apps | Consumption | $0-5 (pay per vCPU-second) |
| Azure Container Registry | Basic | $5 |
| Azure OpenAI (GPT-4o) | Standard S0 | $5-50 (pay per token) |
| Bing Search API | S1 | $5-10 (pay per transaction) |
| **Total** | | **~$15-70/month** |

**Notes:**
- Container Apps scale to zero when idle (no cost)
- OpenAI cost depends on token usage
- Bing Search S1 tier: 1,000 transactions/month included
- Actual costs may vary based on usage patterns

## Production Deployment

For production, use the prod parameter file and consider:

1. **Upgrade SKUs**:
   - ACR: Standard or Premium for geo-replication
   - Container Apps: Dedicated workload profiles for guaranteed resources

2. **Security enhancements**:
   - Disable ACR admin user, use managed identities
   - Add virtual network integration
   - Enable Azure Key Vault for secrets

3. **Monitoring**:
   - Enable Application Insights
   - Configure alerts for errors/latency
   - Set up log analytics workspace

4. **High availability**:
   - Deploy to multiple regions
   - Use Azure Front Door for global load balancing

Deploy production:

```bash
$RESOURCE_GROUP = "rg-travel-agent-prod"

az group create --name $RESOURCE_GROUP --location eastus2

az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file infra/main.bicep `
  --parameters infra/parameters/prod.bicepparam
```

## Troubleshooting

### Issue: Container App not starting

```bash
# View logs
az containerapp logs show `
  --resource-group $RESOURCE_GROUP `
  --name travel-agent-dev-backend `
  --follow
```

### Issue: ACR authentication fails

```bash
# Re-login to ACR
az acr login --name <registry-name>

# Verify credentials
az acr credential show --name <registry-name>
```

### Issue: OpenAI quota errors

Check quota availability in your subscription:
```bash
az cognitiveservices account list-usage `
  --resource-group $RESOURCE_GROUP `
  --name travel-agent-dev-openai
```

## Cleanup

To delete all resources:

```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Bicep Language Reference](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Support

For issues or questions:
- Check Azure Portal for resource status
- Review Container Apps logs
- Consult the team Copilot space for architecture decisions
