@description('The name of the Azure Container Registry')
param name string

@description('Azure region for the resource')
param location string = resourceGroup().location

@description('The SKU of the container registry')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param skuName string = 'Basic'

@description('Tags to apply to the resource')
param tags object = {}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    adminUserEnabled: true
  }
}

@description('The resource ID of the container registry')
output id string = acr.id

@description('The name of the container registry')
output name string = acr.name

@description('The login server URL of the container registry')
output loginServer string = acr.properties.loginServer

@description('The admin username for the container registry')
output adminUsername string = acr.listCredentials().username

@description('The admin password for the container registry')
@secure()
output adminPassword string = acr.listCredentials().passwords[0].value
