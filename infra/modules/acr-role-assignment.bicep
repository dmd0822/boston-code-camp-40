@description('The principal ID to assign the role to')
param principalId string

@description('The role definition ID (full resource ID)')
param roleDefinitionId string

@description('The name of the ACR resource to scope the assignment to')
param acrName string

@description('The type of principal')
@allowed([
  'ServicePrincipal'
  'User'
  'Group'
  'ForeignGroup'
])
param principalType string = 'ServicePrincipal'

@description('Whether to create the role assignment. Set to false to skip.')
param enabled bool = true

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

// Deterministic name: same principal + role + scope = same GUID
var roleAssignmentName = guid(acr.id, principalId, roleDefinitionId)

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enabled && !empty(principalId)) {
  name: roleAssignmentName
  scope: acr
  properties: {
    roleDefinitionId: roleDefinitionId
    principalId: principalId
    principalType: principalType
  }
}

@description('Whether the role assignment was created')
output created bool = enabled && !empty(principalId)
