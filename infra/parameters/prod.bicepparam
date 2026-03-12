using '../main.bicep'

param environmentName = 'prod'
param location = 'westus3'
param deployBingSearch = true

// The resource group to deploy into (must already exist)
// Used by CI/CD workflow: rg-travel-agent-prod
