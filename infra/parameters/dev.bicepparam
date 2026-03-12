using '../main.bicep'

param environmentName = 'dev'
param location = 'westus3'
param deployBingSearch = false

// The resource group to deploy into (must already exist)
// Used by CI/CD workflow: rg-travel-agent-dev
