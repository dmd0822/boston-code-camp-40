@description('The name of the AI Foundry resource')
param name string

@description('Azure region for the resource')
param location string = resourceGroup().location

@description('Tags to apply to the resource')
param tags object = {}

@description('The name of the AI model to deploy')
param modelName string = 'gpt-4o'

@description('The version of the AI model')
param modelVersion string

@description('The name for the model deployment')
param deploymentName string

@description('The SKU name for the model deployment')
param modelSkuName string = 'GlobalStandard'

@description('The capacity (TPM in thousands) for the deployment')
param capacity int = 10

@description('The name of the AI Foundry project')
param projectName string

// AI Foundry account (CognitiveServices kind='AIServices')
resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: name
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

// Project as a child resource of the Foundry account
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  name: projectName
  parent: aiFoundry
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

// Model deployment as a child resource of the Foundry account
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiFoundry
  name: deploymentName
  sku: {
    name: modelSkuName
    capacity: capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

@description('The resource ID of the AI Foundry account')
output id string = aiFoundry.id

@description('The name of the AI Foundry account')
output name string = aiFoundry.name

@description('The endpoint URL for the AI Foundry account')
output endpoint string = aiFoundry.properties.endpoint

@description('The name of the model deployment')
output deploymentName string = modelDeployment.name

@description('The resource ID of the AI Foundry project')
output projectId string = project.id

@description('The name of the AI Foundry project')
output projectName string = project.name

@description('The principal ID of the Foundry managed identity')
output principalId string = aiFoundry.identity.principalId
