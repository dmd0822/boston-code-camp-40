@description('The environment name (e.g., dev, staging, prod)')
param environmentName string = 'dev'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('The version of the GPT-4o model to deploy')
param openaiModelVersion string = '2024-05-13'

@description('The version tag for the application')
param appVersion string = '0.1.0'

// Resource naming convention: travel-agent-{environmentName}-{resource}
var baseName = 'travel-agent-${environmentName}'
var tags = {
  project: 'travel-agent'
  environment: environmentName
}

// ========================================
// Module 1: Azure Container Registry
// ========================================
module acr 'modules/acr.bicep' = {
  name: 'acr-deployment'
  params: {
    name: replace('${baseName}-acr', '-', '')  // ACR names cannot contain hyphens
    location: location
    skuName: 'Basic'
    tags: tags
  }
}

// ========================================
// Module 2: Container Apps Environment
// ========================================
module containerAppEnv 'modules/container-app-env.bicep' = {
  name: 'container-app-env-deployment'
  params: {
    name: '${baseName}-env'
    location: location
    tags: tags
  }
}

// ========================================
// Module 3: AI Foundry (Account + Project + Model)
// ========================================
module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'ai-foundry-deployment'
  params: {
    name: '${baseName}-ai'
    location: location
    projectName: '${baseName}-ai-project'
    modelName: 'gpt-4o'
    modelVersion: openaiModelVersion
    deploymentName: 'gpt-4o'
    capacity: 10
    tags: tags
  }
}

// ========================================
// Module 4: Backend Container App
// ========================================
module backendApp 'modules/container-app.bicep' = {
  name: 'backend-app-deployment'
  params: {
    name: '${baseName}-backend'
    location: location
    environmentId: containerAppEnv.outputs.id
    containerImage: '${acr.outputs.loginServer}/travel-agent-backend:${appVersion}'
    targetPort: 8000
    registryServer: acr.outputs.loginServer
    registryUsername: acr.outputs.adminUsername
    registryPassword: acr.outputs.adminPassword
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 0
    maxReplicas: 3
    secrets: [
      {
        name: 'azure-openai-api-key'
        value: aiFoundry.outputs.key
      }
    ]
    env: [
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: aiFoundry.outputs.endpoint
      }
      {
        name: 'AZURE_OPENAI_API_KEY'
        secretRef: 'azure-openai-api-key'
      }
      {
        name: 'AZURE_OPENAI_DEPLOYMENT'
        value: aiFoundry.outputs.deploymentName
      }
      {
        name: 'APP_VERSION'
        value: appVersion
      }
    ]
    tags: tags
  }
}

// ========================================
// Module 5: Frontend Container App
// ========================================
module frontendApp 'modules/container-app.bicep' = {
  name: 'frontend-app-deployment'
  params: {
    name: '${baseName}-frontend'
    location: location
    environmentId: containerAppEnv.outputs.id
    containerImage: '${acr.outputs.loginServer}/travel-agent-frontend:${appVersion}'
    targetPort: 80
    registryServer: acr.outputs.loginServer
    registryUsername: acr.outputs.adminUsername
    registryPassword: acr.outputs.adminPassword
    cpu: '0.25'
    memory: '0.5Gi'
    minReplicas: 0
    maxReplicas: 3
    secrets: []
    env: [
      {
        name: 'BACKEND_URL'
        value: backendApp.outputs.url
      }
    ]
    tags: tags
  }
}

// ========================================
// Outputs
// ========================================
@description('The URL of the frontend application')
output frontendUrl string = frontendApp.outputs.url

@description('The URL of the backend API')
output backendUrl string = backendApp.outputs.url

@description('The login server for the container registry')
output acrLoginServer string = acr.outputs.loginServer

@description('The AI Foundry endpoint')
output aiFoundryEndpoint string = aiFoundry.outputs.endpoint

@description('The name of the AI Foundry account')
output aiFoundryName string = aiFoundry.outputs.name

@description('The name of the AI Foundry project')
output aiFoundryProjectName string = aiFoundry.outputs.projectName
