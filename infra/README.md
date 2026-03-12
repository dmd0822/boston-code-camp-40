# infra/ — Infrastructure as Code

This folder contains **Bicep templates** for deploying the Travel Agent Application to Azure.

## Status

**Phase 5 (Infrastructure Deployment) — Planned**

Currently a skeleton. Will contain:
- Azure Container Apps for the FastAPI backend
- Azure Container Registry for Docker images
- Azure OpenAI service configuration
- Bing Web Search API wiring
- Network and security policies

## Planned Structure

```
infra/
├── main.bicep              # Main deployment template
├── parameters.json         # Deployment parameters
├── modules/
│   ├── container_app.bicep
│   ├── openai.bicep
│   ├── search_api.bicep
│   └── registry.bicep
└── README-DEPLOY.md        # Deployment instructions
```

## Technology

- **Language:** Bicep (ARM template abstraction)
- **Platform:** Azure Container Apps
- **Services:**
  - Azure OpenAI (GPT-4o)
  - Bing Web Search API
  - Azure Container Registry
  - Key Vault (secrets management)

## Deployment (When Phase 5 Begins)

Expected workflow:

```bash
# Deploy infrastructure
az deployment group create \
  --resource-group my-rg \
  --template-file infra/main.bicep \
  --parameters infra/parameters.json

# Deploy application
az acr build -r my-registry -t travel-agent:latest .
az containerapp update -n travel-agent --image my-registry/travel-agent:latest
```

## Conventions

- **Modular:** One .bicep file per Azure resource
- **Parameterized:** All values in parameters.json, never hard-coded
- **Secrets:** Use Key Vault for API keys, never in templates
- **Documented:** Each template has comments explaining resources

## Security

- No secrets in source code
- Use Azure Key Vault for API keys
- Network security groups restrict access
- Container images scanned for vulnerabilities

## How This Fits

- Runs the FastAPI backend from ntrypoints/serve.py
- Configures environment variables from config/
- Deploys Docker image built from Dockerfile
- Provisions Azure OpenAI and Bing Search APIs

## See Also

- Dockerfile — Container image definition
- ntrypoints/serve.py — Application entry point
- [docs/architecture.md](../docs/architecture.md) — System design
- .squad/decisions.md — Infrastructure decisions
