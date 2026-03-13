using '../main.bicep'

param environmentName = 'dev'
param location = 'westus3'

// Role assignments already exist in this environment — skip to avoid
// RoleAssignmentExists errors from previously-created assignments
param createRoleAssignments = false

// The resource group to deploy into (must already exist)
// Used by CI/CD workflow: rg-travel-agent-dev
