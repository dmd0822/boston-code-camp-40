@description('The name of the Container Apps managed environment')
param name string

@description('Azure region for the resource')
param location string = resourceGroup().location

@description('Tags to apply to the resource')
param tags object = {}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
  }
}

@description('The resource ID of the Container Apps environment')
output id string = containerAppEnv.id

@description('The name of the Container Apps environment')
output name string = containerAppEnv.name
