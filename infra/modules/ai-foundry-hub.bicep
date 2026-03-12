@description('The name of the AI Foundry Hub')
param name string

@description('Azure region for the resource')
param location string = resourceGroup().location

@description('Tags to apply to the resource')
param tags object = {}

@description('Optional storage account resource ID. If not provided, hub will auto-create storage')
param storageAccountId string = ''

@description('Optional key vault resource ID. If not provided, hub will auto-create key vault')
param keyVaultId string = ''

resource hub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: name
  location: location
  tags: tags
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: name
    description: 'AI Foundry Hub for Travel Agent Application'
    // Allow hub to auto-create dependencies if not provided
    storageAccount: !empty(storageAccountId) ? storageAccountId : null
    keyVault: !empty(keyVaultId) ? keyVaultId : null
    publicNetworkAccess: 'Enabled'
  }
}

@description('The resource ID of the AI Foundry Hub')
output id string = hub.id

@description('The name of the AI Foundry Hub')
output name string = hub.name

@description('The principal ID of the hub managed identity')
output principalId string = hub.identity.principalId
