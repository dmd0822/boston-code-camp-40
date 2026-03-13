# Travel Agent Application - Azure Infrastructure

This directory contains the Infrastructure as Code (IaC) for deploying
the Travel Agent Application to Azure with Bicep, Azure Container Apps,
and Azure AI Foundry.

## Architecture Overview

The deployment centers on a resource group that hosts the application,
runtime identities, and Azure AI resources:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Resource Group                           │
│                                                                     │
│  ┌──────────────────┐      ┌─────────────────────────────────────┐  │
│  │ User-Assigned    │      │ Azure Container Apps Environment    │  │
│  │ Identity         │─────▶│                                     │  │
│  │ (ACR pull)       │      │  ┌──────────────┐  ┌──────────────┐ │  │
│  └────────┬─────────┘      │  │ Frontend App │  │ Backend App  │ │  │
│           │                │  │ nginx + SPA  │  │ FastAPI      │ │  │
│           ▼                │  └──────┬───────┘  └──────┬───────┘ │  │
│  ┌──────────────────┐      └─────────│──────────────────│────────┘  │
│  │ Azure Container  │                │                  │           │
│  │ Registry (ACR)   │◀───────────────┘                  │           │
│  │ admin disabled   │                                   │           │
│  └──────────────────┘                                   │           │
│                                                         ▼           │
│                                            ┌──────────────────────┐ │
│                                            │ Azure AI Foundry     │ │
│                                            │ Account + Project    │ │
│                                            │ + GPT-4o deployment  │ │
│                                            └──────────────────────┘ │
│                                                         │           │
│                                                         ▼           │
│                                            ┌──────────────────────┐ │
│                                            │ Optional Bing Search │ │
│                                            │ integration module   │ │
│                                            └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

1. **`acr.bicep`** — Azure Container Registry with admin access disabled
2. **`container-app-env.bicep`** — Shared Container Apps environment
3. **`container-app.bicep`** — Reusable frontend/backend Container App
   module
4. **`ai-foundry.bicep`** — Combined AI Services account, AI Foundry
   project, and model deployment
5. **`bing-search.bicep`** — Bing Search resource module for optional
   search-backed scenarios
6. **`role-assignment.bicep`** — Resource-group-scoped role assignment
   helper with deterministic naming
7. **`acr-role-assignment.bicep`** — ACR-scoped role assignment helper
   for `AcrPull`

### Key Features

- **Managed identity first**: The backend authenticates with
  `DefaultAzureCredential`; local dev uses Azure CLI and Azure uses
  managed identity
- **ACR admin disabled**: `adminUserEnabled: false` and image pulls use a
  user-assigned identity instead of registry passwords
- **Reusable RBAC modules**: Role assignment modules support
  deterministic GUID names and conditional creation via `enabled`
- **Runtime AI integration**: The backend calls Azure AI Foundry Agent
  Service at runtime through the project endpoint, not just for
  governance
- **OIDC-ready deployment**: GitHub Actions uses Azure federated
  credentials for infra and app deployment

## Validation and Testing

The current infrastructure validation suite covers **109 passing checks**
across Bicep validation and Dockerfile verification. An additional
**4 Docker build checks are skipped** automatically when a Docker daemon
is unavailable.

Run the infra tests from the repository root:

```bash
pytest tests/infra/
pytest tests/infra/ -m "not docker_build"
```

## Azure AI Foundry Runtime Model

This project now treats Azure AI Foundry as both the deployment target
and the runtime dependency for agent execution.

### What `ai-foundry.bicep` provisions

- An **Azure AI Services account** (`kind: AIServices`)
- An **AI Foundry project** as a child resource
- A **GPT-4o model deployment** for agent execution
- `disableLocalAuth: true`, so application code uses Azure Identity
  instead of service keys

### How the backend connects

At runtime the backend creates `AzureAIClient` with:

- `project_endpoint=AZURE_AI_PROJECT_ENDPOINT`
- `model_deployment_name=AZURE_AI_MODEL_DEPLOYMENT_NAME`
- `credential=DefaultAzureCredential()`

That means:
- **Local development** uses `az login` → `AzureCliCredential`
- **Azure Container Apps** uses the backend's system-assigned managed
  identity
- The backend managed identity needs the **Azure AI User** role
  (`53ca6127-db72-4b80-b1b0-d745d6d5456d`) at resource-group scope

AI Foundry is no longer just a management layer for this app; it is the
backend's live agent runtime.

## Prerequisites

Before deploying, ensure you have:

1. **Azure CLI** (v2.50.0 or later)
   ```bash
   az --version
   ```
2. **Bicep CLI** (bundled with Azure CLI)
   ```bash
   az bicep version
   ```
3. **Docker** for image builds
   ```bash
   docker --version
   ```
4. **Azure subscription** with permission to deploy resource-group
   resources and role assignments
5. **Azure login**
   ```bash
   az login
   az account set --subscription <subscription-id>
   ```
6. **Optional Bing provider registration** if you plan to use the Bing
   module in your environment
   ```bash
   az provider register --namespace Microsoft.Bing
   ```

## Deployment Guide

### Step 1: Create the resource group

The resource group must already exist. Environment names and locations
are defined in `infra/environments.json`.

```bash
$RESOURCE_GROUP = "rg-travel-agent-dev"
$LOCATION = "westus3"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 2: Deploy infrastructure

Deploy with the current Bicep parameter files:

```bash
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam
```

Capture useful outputs:

```bash
$OUTPUTS = az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs \
  --output json | ConvertFrom-Json

$ACR_LOGIN_SERVER = $OUTPUTS.acrLoginServer.value
$FRONTEND_URL = $OUTPUTS.frontendUrl.value
$BACKEND_URL = $OUTPUTS.backendUrl.value
$PROJECT_ENDPOINT = $OUTPUTS.aiFoundryProjectEndpoint.value
```

### Step 3: Build and push Docker images

#### Backend image

```bash
cd C:\repos\boston-code-camp-40
az acr login --name $ACR_LOGIN_SERVER.Split('.')[0]

docker build -t "${ACR_LOGIN_SERVER}/travel-agent-backend:0.1.0" .
docker push "${ACR_LOGIN_SERVER}/travel-agent-backend:0.1.0"
```

#### Frontend image

```bash
docker build -t "${ACR_LOGIN_SERVER}/travel-agent-frontend:0.1.0" \
  -f src/frontend/Dockerfile src/frontend/
docker push "${ACR_LOGIN_SERVER}/travel-agent-frontend:0.1.0"
```

### Step 4: Update Container Apps

Container Apps pull from ACR using the user-assigned identity created
for image pull access. No registry username or password is configured on
the app module.

```bash
az containerapp update \
  --resource-group $RESOURCE_GROUP \
  --name travel-agent-dev-backend \
  --image "${ACR_LOGIN_SERVER}/travel-agent-backend:0.1.0"

az containerapp update \
  --resource-group $RESOURCE_GROUP \
  --name travel-agent-dev-frontend \
  --image "${ACR_LOGIN_SERVER}/travel-agent-frontend:0.1.0" \
  --set-env-vars "BACKEND_URL=$BACKEND_URL"
```

### Step 5: Test the deployment

```bash
curl "$BACKEND_URL/api/health"
Start-Process $FRONTEND_URL
```

## Environment Variables Reference

### Backend Container App

| Variable | Source | Type | Description |
|----------|--------|------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` | `ai-foundry.bicep` output | Regular | Azure AI Foundry project endpoint (`services.ai.azure.com`) |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | `ai-foundry.bicep` output | Regular | Model deployment name used by `AzureAIClient` |
| `APP_VERSION` | Deployment/pipeline input | Regular | Application version exposed by `/api/health` |

### Frontend Container App

| Variable | Source | Type | Description |
|----------|--------|------|-------------|
| `BACKEND_URL` | Backend app output | Regular | HTTPS backend base URL proxied by nginx |
| `BACKEND_HOST` | Derived in `entrypoint.sh` | Runtime | Hostname extracted from `BACKEND_URL` for TLS SNI and `Host` header forwarding |

## Module Reference

### `modules/acr.bicep`
Creates Azure Container Registry with admin access disabled.

**Key parameters:** `name`, `location`, `skuName`, `tags`

**Outputs:** `id`, `name`, `loginServer`

### `modules/container-app-env.bicep`
Creates the shared Container Apps managed environment.

**Key parameters:** `name`, `location`, `tags`

**Outputs:** `id`, `name`

### `modules/container-app.bicep`
Reusable module for frontend and backend Container Apps.

**Key parameters:**
- `name`, `location`, `environmentId`, `targetPort`
- `containerImage`, `env`, `secrets`
- `registryServer`, `userAssignedIdentityId`
- `cpu`, `memory`, `minReplicas`, `maxReplicas`, `tags`

**Outputs:** `id`, `name`, `fqdn`, `url`, `principalId`

**Notes:**
- Assigns **both** system-assigned and user-assigned identities
- Pulls container images from ACR via identity, not registry passwords

### `modules/ai-foundry.bicep`
Creates the Azure AI Services account, AI Foundry project, and model
deployment in one module.

**Key parameters:**
- `name`, `location`, `projectName`, `tags`
- `modelName`, `modelVersion`, `deploymentName`
- `modelSkuName`, `capacity`

**Outputs:**
- `id`, `name`, `endpoint`
- `projectEndpoint`, `projectId`, `projectName`
- `deploymentName`, `principalId`

**Notes:**
- Replaces the older separate OpenAI / hub / project / connection module
  stack
- Sets `disableLocalAuth: true` so runtime access goes through Azure
  Identity

### `modules/bing-search.bicep`
Creates a Bing Search resource for optional search-backed scenarios.

**Key parameters:** `name`, `skuName`, `tags`

**Outputs:** `id`, `endpoint`

### `modules/role-assignment.bicep`
Reusable resource-group-scoped role assignment helper.

**Key parameters:**
- `principalId`, `roleDefinitionId`, `principalType`
- `scopeSeed`, `roleDescription`, `enabled`

**Outputs:** `name`, `created`

**Notes:**
- Uses a deterministic GUID so repeated deployments stay idempotent
- Supports conditional creation with `enabled`

### `modules/acr-role-assignment.bicep`
Reusable ACR-scoped role assignment helper.

**Key parameters:**
- `principalId`, `roleDefinitionId`, `acrName`
- `principalType`, `enabled`

**Outputs:** `created`

## Parameter Files

Current parameter files live under `infra/parameters/`:

- `dev.bicepparam`
- `prod.bicepparam`

These replace the older `main.parameters.*.json` files.

## Cost Estimates (Dev Tier)

Approximate monthly costs for a light dev environment:

| Resource | SKU/Tier | Estimated Cost |
|----------|----------|----------------|
| Azure Container Apps | Consumption | $0-5 |
| Azure Container Registry | Basic | $5 |
| Azure AI Foundry / AI Services | S0 + GPT-4o usage | $5-50 |
| Bing Search API | S1 | $5-10 |
| **Total** | | **~$15-70/month** |

**Notes:**
- Container Apps scale to zero when idle
- AI Foundry usage is primarily model-consumption driven
- Bing Search remains optional by environment and subscription support

## Production Deployment

For production, use `infra/parameters/prod.bicepparam` and consider:

1. **Capacity and scale**
   - Increase Container Apps limits and replica counts as needed
   - Adjust AI deployment capacity for expected request volume
2. **Security**
   - Keep ACR admin disabled (already the default)
   - Add private networking or ingress restrictions where required
   - Review RBAC assignments and disable creation once stabilized
3. **Observability**
   - Add or extend Azure Monitor / Log Analytics integration
   - Configure alerts for latency, failed revisions, and deployment drift
4. **Availability**
   - Consider multi-region patterns and global routing when needed

Deploy production:

```bash
az deployment group create \
  --resource-group rg-travel-agent-prod \
  --template-file infra/main.bicep \
  --parameters infra/parameters/prod.bicepparam
```

## Troubleshooting

### Issue: Container App not starting

```bash
az containerapp logs show \
  --resource-group $RESOURCE_GROUP \
  --name travel-agent-dev-backend \
  --follow
```

### Issue: ACR pull fails

Check that the user-assigned identity has `AcrPull` on the registry and
that the Container App is configured with the expected identity:

```bash
az role assignment list \
  --scope $(az acr show -n <acr-name> --query id -o tsv) \
  --assignee <principal-id> \
  --output table
```

### Issue: Backend cannot call Azure AI Foundry

Verify the backend system-assigned identity has the **Azure AI User**
role on the resource group and confirm the project endpoint value:

```bash
az role assignment list \
  --resource-group $RESOURCE_GROUP \
  --assignee <backend-principal-id> \
  --output table
```

## Cleanup

To remove the environment:

```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Bicep Language Reference](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Support

For issues or questions:
- Check Azure Portal for resource status
- Review Container Apps logs and deployment outputs
- Consult the team Copilot space for architecture decisions
