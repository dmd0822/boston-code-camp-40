@description('The principal ID to assign the role to')
param principalId string

@description('The role definition ID (full resource ID)')
param roleDefinitionId string

@description('The type of principal')
@allowed([
  'ServicePrincipal'
  'User'
  'Group'
  'ForeignGroup'
])
param principalType string = 'ServicePrincipal'

@description('Scope resource ID used in the deterministic GUID (e.g., resource group ID, resource ID)')
param scopeSeed string = resourceGroup().id

@description('Optional description for the role assignment')
param roleDescription string = ''

@description('Whether to create the role assignment. Set to false to skip if it already exists.')
param enabled bool = true

// Deterministic name ensures idempotency: same principal + role + scope = same GUID
var roleAssignmentName = guid(scopeSeed, principalId, roleDefinitionId)

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enabled && !empty(principalId)) {
  name: roleAssignmentName
  properties: {
    roleDefinitionId: roleDefinitionId
    principalId: principalId
    principalType: principalType
    description: !empty(roleDescription) ? roleDescription : null
  }
}

@description('The name (GUID) of the role assignment')
output name string = enabled && !empty(principalId) ? roleAssignment.name : ''

@description('Whether the role assignment was created')
output created bool = enabled && !empty(principalId)
