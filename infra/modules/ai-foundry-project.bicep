@description('The name of the AI Foundry Project')
param name string

@description('Azure region for the resource')
param location string = resourceGroup().location

@description('The resource ID of the parent AI Foundry Hub')
param hubId string

@description('Tags to apply to the resource')
param tags object = {}

resource project 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: name
  location: location
  tags: tags
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: name
    description: 'AI Foundry Project for Travel Agent Application'
    hubResourceId: hubId
    publicNetworkAccess: 'Enabled'
  }
}

@description('The resource ID of the AI Foundry Project')
output id string = project.id

@description('The name of the AI Foundry Project')
output name string = project.name

@description('The principal ID of the project managed identity')
output principalId string = project.identity.principalId
