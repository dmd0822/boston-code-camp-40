@description('The name of the AI Foundry Hub')
param hubName string

@description('The name of the connection')
param connectionName string

@description('The Azure OpenAI endpoint URL')
param openaiEndpoint string

@description('The Azure OpenAI API key')
@secure()
param openaiApiKey string

@description('The resource ID of the Azure OpenAI account')
param openaiResourceId string

resource hub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' existing = {
  name: hubName
}

resource openaiConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-04-01' = {
  parent: hub
  name: connectionName
  properties: {
    category: 'AzureOpenAI'
    target: openaiEndpoint
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: openaiApiKey
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: openaiResourceId
    }
  }
}

@description('The resource ID of the OpenAI connection')
output id string = openaiConnection.id

@description('The name of the OpenAI connection')
output name string = openaiConnection.name
