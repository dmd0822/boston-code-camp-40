@description('The environment name (e.g., dev, staging, prod)')
param environmentName string = 'dev'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('The version of the GPT-4o model to deploy')
param openaiModelVersion string = '2024-05-13'

@description('Whether to create role assignments (set false if they already exist)')
param createRoleAssignments bool = true

// Resource naming convention: travel-agent-{environmentName}-{resource}
var baseName = 'travel-agent-${environmentName}'
var tags = {
  project: 'travel-agent'
  environment: environmentName
}

// Well-known Azure role definition IDs
var acrPullRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
var azureAIUserRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')

// ========================================
// User-Assigned Managed Identity (for ACR pull)
// ========================================
resource acrPullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${baseName}-acr-pull'
  location: location
  tags: tags
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
// Role: AcrPull for the managed identity on ACR
// ========================================
module acrPullRole 'modules/acr-role-assignment.bicep' = {
  name: 'acr-pull-role-assignment'
  params: {
    principalId: acrPullIdentity.properties.principalId
    roleDefinitionId: acrPullRoleId
    acrName: replace('${baseName}-acr', '-', '')
    enabled: createRoleAssignments
  }
  dependsOn: [acr]
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
    capacity: 80
    tags: tags
  }
}

// ========================================
// Module 4: Backend Container App
// ========================================
module backendApp 'modules/container-app.bicep' = {
  name: 'backend-app-deployment'
  dependsOn: [acrPullRole]
  params: {
    name: '${baseName}-backend'
    location: location
    environmentId: containerAppEnv.outputs.id
    targetPort: 8000
    registryServer: acr.outputs.loginServer
    userAssignedIdentityId: acrPullIdentity.id
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 0
    maxReplicas: 3
    secrets: []
    env: [
      {
        name: 'AZURE_AI_PROJECT_ENDPOINT'
        value: aiFoundry.outputs.projectEndpoint
      }
      {
        name: 'AZURE_AI_MODEL_DEPLOYMENT_NAME'
        value: aiFoundry.outputs.deploymentName
      }
    ]
    tags: tags
  }
}

// ========================================
// Role: Azure AI User for backend on AI Foundry (resource group scope)
// ========================================
module backendAIRole 'modules/role-assignment.bicep' = {
  name: 'backend-ai-user-role-assignment'
  params: {
    principalId: backendApp.outputs.principalId
    roleDefinitionId: azureAIUserRoleId
    description: 'Grants backend container app access to AI Foundry Agent Service'
    enabled: createRoleAssignments
  }
}

// ========================================
// Module 5: Frontend Container App
// ========================================
module frontendApp 'modules/container-app.bicep' = {
  name: 'frontend-app-deployment'
  dependsOn: [acrPullRole]
  params: {
    name: '${baseName}-frontend'
    location: location
    environmentId: containerAppEnv.outputs.id
    targetPort: 80
    registryServer: acr.outputs.loginServer
    userAssignedIdentityId: acrPullIdentity.id
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

@description('The AI Foundry project endpoint')
output aiFoundryProjectEndpoint string = aiFoundry.outputs.projectEndpoint

@description('The name of the AI Foundry account')
output aiFoundryName string = aiFoundry.outputs.name

@description('The name of the AI Foundry project')
output aiFoundryProjectName string = aiFoundry.outputs.projectName
