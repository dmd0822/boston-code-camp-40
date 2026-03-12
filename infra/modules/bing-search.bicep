@description('The name of the Bing Search resource')
param name string

@description('The SKU name for Bing Search')
@allowed([
  'S1'
  'S2'
  'S3'
  'S4'
  'S5'
  'S6'
  'S7'
  'S8'
  'S9'
])
param skuName string = 'S1'

@description('Tags to apply to the resource')
param tags object = {}

resource bingSearch 'Microsoft.Bing/accounts@2020-06-10' = {
  name: name
  location: 'global'
  tags: tags
  kind: 'Bing.Search.v7'
  sku: {
    name: skuName
  }
  properties: {}
}

@description('The resource ID of the Bing Search account')
output id string = bingSearch.id

@description('The endpoint URL for Bing Search')
output endpoint string = 'https://api.bing.microsoft.com/v7.0/search'

@description('The API key for the Bing Search resource')
@secure()
output key string = bingSearch.listKeys().key1
