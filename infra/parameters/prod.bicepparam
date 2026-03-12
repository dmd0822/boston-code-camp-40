using '../main.bicep'

param environmentName = 'prod'
param location = 'eastus2'

// The resource group to deploy into (must already exist)
// Used by CI/CD workflow: rg-travel-agent-prod
