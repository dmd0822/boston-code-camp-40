@description('The name of the Azure OpenAI resource')
param name string

@description('Azure region for the resource')
param location string = resourceGroup().location

@description('The SKU name for the OpenAI resource')
param skuName string = 'S0'

@description('The name of the AI model to deploy')
param modelName string = 'gpt-4o'

@description('The version of the AI model')
param modelVersion string

@description('The name for the model deployment')
param deploymentName string

@description('The capacity (TPM in thousands) for the deployment')
param capacity int = 10

@description('Tags to apply to the resource')
param tags object = {}

resource openai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: skuName
  }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
  }
}

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openai
  name: deploymentName
  sku: {
    name: 'Standard'
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

@description('The resource ID of the OpenAI account')
output id string = openai.id

@description('The endpoint URL for the OpenAI resource')
output endpoint string = openai.properties.endpoint

@description('The API key for the OpenAI resource')
@secure()
output key string = openai.listKeys().key1

@description('The name of the model deployment')
output deploymentName string = deployment.name
