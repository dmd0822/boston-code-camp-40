"""
Validation tests for Bicep infrastructure as code files.

These tests validate that the Bicep files are correctly structured
and contain all required configurations for Azure deployment.
"""

from pathlib import Path
import re
import pytest


class TestMainBicep:
    """Tests for the main.bicep orchestration file."""

    @pytest.fixture
    def main_bicep_path(self) -> Path:
        """Path to main.bicep file."""
        return Path(__file__).parent.parent.parent / "infra" / "main.bicep"

    @pytest.fixture
    def main_bicep_content(self, main_bicep_path: Path) -> str:
        """Read main.bicep content."""
        return main_bicep_path.read_text()

    def test_main_bicep_exists(self, main_bicep_path: Path):
        """Test that main.bicep exists and is not empty."""
        assert main_bicep_path.exists(), "main.bicep does not exist"
        assert main_bicep_path.stat().st_size > 0, "main.bicep is empty"

    def test_has_environment_name_parameter(self, main_bicep_content: str):
        """Test that main.bicep has environmentName parameter."""
        assert re.search(r"param\s+environmentName\s+string", main_bicep_content), \
            "main.bicep should have environmentName parameter"

    def test_has_location_parameter(self, main_bicep_content: str):
        """Test that main.bicep has location parameter."""
        assert re.search(r"param\s+location\s+string", main_bicep_content), \
            "main.bicep should have location parameter"

    def test_resource_group_scoped(self, main_bicep_content: str):
        """Test that main.bicep is resource-group scoped (no targetScope)."""
        assert "targetScope" not in main_bicep_content, \
            "main.bicep should not set targetScope (defaults to resourceGroup)"

    def test_location_defaults_to_resource_group(self, main_bicep_content: str):
        """Test that location defaults to resourceGroup().location."""
        assert "resourceGroup().location" in main_bicep_content, \
            "location should default to resourceGroup().location"

    def test_has_project_tag(self, main_bicep_content: str):
        """Test that main.bicep defines project tag."""
        assert re.search(r"project:\s*['\"]travel-agent['\"]", main_bicep_content), \
            "main.bicep should define project: 'travel-agent' tag"

    def test_references_acr_module(self, main_bicep_content: str):
        """Test that main.bicep references acr.bicep module."""
        assert "modules/acr.bicep" in main_bicep_content, \
            "main.bicep should reference modules/acr.bicep"

    def test_references_container_app_env_module(self, main_bicep_content: str):
        """Test that main.bicep references container-app-env.bicep module."""
        assert "modules/container-app-env.bicep" in main_bicep_content, \
            "main.bicep should reference modules/container-app-env.bicep"

    def test_references_container_app_module(self, main_bicep_content: str):
        """Test that main.bicep references container-app.bicep module."""
        assert "modules/container-app.bicep" in main_bicep_content, \
            "main.bicep should reference modules/container-app.bicep"

    def test_references_ai_foundry_module(self, main_bicep_content: str):
        """Test that main.bicep references ai-foundry.bicep module."""
        assert "modules/ai-foundry.bicep" in main_bicep_content, \
            "main.bicep should reference modules/ai-foundry.bicep"

    def test_does_not_reference_standalone_openai(self, main_bicep_content: str):
        """Test that main.bicep does not reference standalone openai.bicep."""
        assert "modules/openai.bicep" not in main_bicep_content, \
            "main.bicep should not reference standalone openai.bicep"

    def test_does_not_reference_bing_search(self, main_bicep_content: str):
        """Test that main.bicep does not reference bing-search module."""
        assert "bing-search.bicep" not in main_bicep_content, \
            "main.bicep should not reference bing-search.bicep"

    def test_passes_azure_openai_endpoint(self, main_bicep_content: str):
        """Test that AZURE_OPENAI_ENDPOINT is passed to backend."""
        assert re.search(r"name:\s*['\"]AZURE_OPENAI_ENDPOINT['\"]", main_bicep_content), \
            "main.bicep should pass AZURE_OPENAI_ENDPOINT to backend"

    def test_no_api_key_env_var(self, main_bicep_content: str):
        """Test that AZURE_OPENAI_API_KEY is not passed (managed identity)."""
        assert "AZURE_OPENAI_API_KEY" not in main_bicep_content, \
            "main.bicep should not pass AZURE_OPENAI_API_KEY (uses managed identity)"

    def test_passes_azure_openai_deployment(self, main_bicep_content: str):
        """Test that AZURE_OPENAI_DEPLOYMENT is passed to backend."""
        assert re.search(r"name:\s*['\"]AZURE_OPENAI_DEPLOYMENT['\"]", main_bicep_content), \
            "main.bicep should pass AZURE_OPENAI_DEPLOYMENT to backend"

    def test_no_bing_search_env_vars(self, main_bicep_content: str):
        """Test that Bing Search env vars are not in main.bicep."""
        assert "BING_SEARCH_ENDPOINT" not in main_bicep_content, \
            "main.bicep should not have BING_SEARCH_ENDPOINT"
        assert "BING_SEARCH_API_KEY" not in main_bicep_content, \
            "main.bicep should not have BING_SEARCH_API_KEY"

    def test_no_bing_search_output(self, main_bicep_content: str):
        """Test that main.bicep has no bingSearchEndpoint output."""
        assert "bingSearchEndpoint" not in main_bicep_content, \
            "main.bicep should not have bingSearchEndpoint output"

    def test_outputs_frontend_url(self, main_bicep_content: str):
        """Test that main.bicep outputs frontendUrl."""
        assert re.search(r"output\s+frontendUrl\s+string", main_bicep_content), \
            "main.bicep should output frontendUrl"

    def test_outputs_backend_url(self, main_bicep_content: str):
        """Test that main.bicep outputs backendUrl."""
        assert re.search(r"output\s+backendUrl\s+string", main_bicep_content), \
            "main.bicep should output backendUrl"

    def test_outputs_acr_login_server(self, main_bicep_content: str):
        """Test that main.bicep outputs acrLoginServer."""
        assert re.search(r"output\s+acrLoginServer\s+string", main_bicep_content), \
            "main.bicep should output acrLoginServer"


class TestContainerAppEnvModule:
    """Tests for the container-app-env.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to container-app-env.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "container-app-env.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_module_exists(self, module_path: Path):
        """Test that container-app-env.bicep exists."""
        assert module_path.exists(), "container-app-env.bicep does not exist"
        assert module_path.stat().st_size > 0, "container-app-env.bicep is empty"

    def test_has_description_decorators(self, module_content: str):
        """Test that parameters have @description decorators."""
        assert "@description(" in module_content, \
            "Module should have @description decorators on parameters"

    def test_creates_managed_environment(self, module_content: str):
        """Test that module creates Microsoft.App/managedEnvironments resource."""
        assert "Microsoft.App/managedEnvironments" in module_content, \
            "Module should create Microsoft.App/managedEnvironments resource"

    def test_has_output_declarations(self, module_content: str):
        """Test that module has output declarations."""
        assert re.search(r"output\s+\w+", module_content), \
            "Module should have output declarations"


class TestContainerAppModule:
    """Tests for the container-app.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to container-app.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "container-app.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_module_exists(self, module_path: Path):
        """Test that container-app.bicep exists."""
        assert module_path.exists(), "container-app.bicep does not exist"
        assert module_path.stat().st_size > 0, "container-app.bicep is empty"

    def test_has_description_decorators(self, module_content: str):
        """Test that parameters have @description decorators."""
        assert "@description(" in module_content, \
            "Module should have @description decorators on parameters"

    def test_creates_container_app(self, module_content: str):
        """Test that module creates Microsoft.App/containerApps resource."""
        assert "Microsoft.App/containerApps" in module_content, \
            "Module should create Microsoft.App/containerApps resource"

    def test_has_ingress_config(self, module_content: str):
        """Test that module has ingress configuration."""
        assert "ingress" in module_content, \
            "Module should have ingress configuration"

    def test_has_secrets_support(self, module_content: str):
        """Test that module supports secrets."""
        assert re.search(r"param\s+secrets\s+array", module_content), \
            "Module should have secrets parameter"
        assert "secrets:" in module_content, \
            "Module should configure secrets in resource"

    def test_has_managed_identity(self, module_content: str):
        """Test that module configures managed identity."""
        assert "identity:" in module_content, \
            "Module should have identity block"
        assert "SystemAssigned" in module_content, \
            "Module should use SystemAssigned identity"

    def test_has_user_assigned_identity_param(self, module_content: str):
        """Test that module has userAssignedIdentityId parameter."""
        assert re.search(
            r"param\s+userAssignedIdentityId\s+string", module_content
        ), "Module should have userAssignedIdentityId parameter"

    def test_no_registry_credentials(self, module_content: str):
        """Test that module does not use registry credentials."""
        assert "registryUsername" not in module_content, \
            "Module should not have registryUsername parameter"
        assert "registryPassword" not in module_content, \
            "Module should not have registryPassword parameter"
        assert "passwordSecretRef" not in module_content, \
            "Module should not use passwordSecretRef for registry"

    def test_registry_uses_identity(self, module_content: str):
        """Test that registry pull uses managed identity."""
        assert re.search(
            r"identity:\s*userAssignedIdentityId", module_content
        ), "Registry config should use identity-based pull"

    def test_outputs_principal_id(self, module_content: str):
        """Test that module outputs principalId for role assignments."""
        assert re.search(r"output\s+principalId\s+string", module_content), \
            "Module should output principalId"

    def test_container_image_optional(self, module_content: str):
        """Test that containerImage param defaults to empty string."""
        assert re.search(
            r"param\s+containerImage\s+string\s*=\s*''", module_content
        ), "containerImage should default to empty string"

    def test_uses_placeholder_when_no_image(self, module_content: str):
        """Test that a placeholder image is used when no image specified."""
        assert "mcr.microsoft.com" in module_content, \
            "Module should use an MCR placeholder image as fallback"

    def test_no_specific_app_image_in_main(self):
        """Test that main.bicep does not specify container images from ACR."""
        main_content = (
            Path(__file__).parent.parent.parent / "infra" / "main.bicep"
        ).read_text()
        assert "containerImage:" not in main_content, \
            "main.bicep should not pass containerImage (handled by app workflow)"
        assert "appVersion" not in main_content, \
            "main.bicep should not reference appVersion"

    def test_has_output_declarations(self, module_content: str):
        """Test that module has output declarations."""
        assert re.search(r"output\s+\w+", module_content), \
            "Module should have output declarations"


class TestACRModule:
    """Tests for the acr.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to acr.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "acr.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_module_exists(self, module_path: Path):
        """Test that acr.bicep exists."""
        assert module_path.exists(), "acr.bicep does not exist"
        assert module_path.stat().st_size > 0, "acr.bicep is empty"

    def test_has_description_decorators(self, module_content: str):
        """Test that parameters have @description decorators."""
        assert "@description(" in module_content, \
            "Module should have @description decorators on parameters"

    def test_creates_container_registry(self, module_content: str):
        """Test that module creates Microsoft.ContainerRegistry/registries resource."""
        assert "Microsoft.ContainerRegistry/registries" in module_content, \
            "Module should create Microsoft.ContainerRegistry/registries resource"

    def test_admin_user_disabled(self, module_content: str):
        """Test that adminUserEnabled is false (managed identity)."""
        assert re.search(r"adminUserEnabled:\s*false", module_content), \
            "Module should set adminUserEnabled: false"

    def test_no_admin_credentials_output(self, module_content: str):
        """Test that module does not output admin credentials."""
        assert "listCredentials" not in module_content, \
            "Module should not use listCredentials() (managed identity)"
        assert "adminUsername" not in module_content or \
            "output adminUsername" not in module_content, \
            "Module should not output adminUsername"
        assert "adminPassword" not in module_content or \
            "output adminPassword" not in module_content, \
            "Module should not output adminPassword"

    def test_has_output_declarations(self, module_content: str):
        """Test that module has output declarations."""
        assert re.search(r"output\s+\w+", module_content), \
            "Module should have output declarations"


class TestAIFoundryModule:
    """Tests for the ai-foundry.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to ai-foundry.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "ai-foundry.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_module_exists(self, module_path: Path):
        """Test that ai-foundry.bicep exists."""
        assert module_path.exists(), "ai-foundry.bicep does not exist"
        assert module_path.stat().st_size > 0, "ai-foundry.bicep is empty"

    def test_has_description_decorators(self, module_content: str):
        """Test that parameters have @description decorators."""
        assert "@description(" in module_content, \
            "Module should have @description decorators on parameters"

    def test_creates_cognitive_services_account(self, module_content: str):
        """Test that module creates Microsoft.CognitiveServices/accounts resource."""
        assert "Microsoft.CognitiveServices/accounts" in module_content, \
            "Module should create Microsoft.CognitiveServices/accounts resource"

    def test_kind_is_ai_services(self, module_content: str):
        """Test that kind is 'AIServices' (not standalone OpenAI)."""
        assert re.search(r"kind:\s*['\"]AIServices['\"]", module_content), \
            "Module should set kind: 'AIServices'"

    def test_allows_project_management(self, module_content: str):
        """Test that allowProjectManagement is true."""
        assert re.search(r"allowProjectManagement:\s*true", module_content), \
            "Module should set allowProjectManagement: true"

    def test_has_system_identity(self, module_content: str):
        """Test that identity type is SystemAssigned."""
        assert re.search(r"type:\s*['\"]SystemAssigned['\"]", module_content), \
            "Module should have identity type: 'SystemAssigned'"

    def test_has_project_child_resource(self, module_content: str):
        """Test that module creates a project child resource."""
        assert "Microsoft.CognitiveServices/accounts/projects" in module_content, \
            "Module should create a project child resource"

    def test_has_model_deployment(self, module_content: str):
        """Test that module creates a model deployment."""
        assert "Microsoft.CognitiveServices/accounts/deployments" in module_content, \
            "Module should create a model deployment child resource"

    def test_has_name_param(self, module_content: str):
        """Test that module has name parameter."""
        assert re.search(r"param\s+name\s+string", module_content), \
            "Module should have name parameter"

    def test_has_location_param(self, module_content: str):
        """Test that module has location parameter."""
        assert re.search(r"param\s+location\s+string", module_content), \
            "Module should have location parameter"

    def test_has_model_name_param(self, module_content: str):
        """Test that module has modelName parameter."""
        assert re.search(r"param\s+modelName\s+string", module_content), \
            "Module should have modelName parameter"

    def test_has_project_name_param(self, module_content: str):
        """Test that module has projectName parameter."""
        assert re.search(r"param\s+projectName\s+string", module_content), \
            "Module should have projectName parameter"

    def test_outputs_endpoint(self, module_content: str):
        """Test that module outputs endpoint."""
        assert re.search(r"output\s+endpoint\s+string", module_content), \
            "Module should output endpoint"

    def test_disable_local_auth(self, module_content: str):
        """Test that disableLocalAuth is true (managed identity)."""
        assert re.search(r"disableLocalAuth:\s*true", module_content), \
            "Module should set disableLocalAuth: true"

    def test_no_key_output(self, module_content: str):
        """Test that module does not output API key (managed identity)."""
        assert not re.search(
            r"output\s+key\s+string", module_content
        ), "Module should not output key (uses managed identity)"
        assert "listKeys" not in module_content, \
            "Module should not use listKeys() (uses managed identity)"

    def test_outputs_deployment_name(self, module_content: str):
        """Test that module outputs deploymentName."""
        assert re.search(r"output\s+deploymentName\s+string", module_content), \
            "Module should output deploymentName"

    def test_outputs_project_name(self, module_content: str):
        """Test that module outputs projectName."""
        assert re.search(r"output\s+projectName\s+string", module_content), \
            "Module should output projectName"

    def test_outputs_id(self, module_content: str):
        """Test that module outputs id."""
        assert re.search(r"output\s+id\s+string", module_content), \
            "Module should output id"

    def test_outputs_principal_id(self, module_content: str):
        """Test that module outputs principalId."""
        assert re.search(r"output\s+principalId\s+string", module_content), \
            "Module should output principalId"

    def test_no_standalone_openai_kind(self, module_content: str):
        """Test that module does not use standalone OpenAI kind."""
        assert not re.search(r"kind:\s*['\"]OpenAI['\"]", module_content), \
            "Module should not use kind: 'OpenAI' (use AIServices instead)"


class TestMainBicepFoundryIntegration:
    """Tests for AI Foundry integration in main.bicep."""

    @pytest.fixture
    def main_bicep_path(self) -> Path:
        """Path to main.bicep file."""
        return Path(__file__).parent.parent.parent / "infra" / "main.bicep"

    @pytest.fixture
    def main_bicep_content(self, main_bicep_path: Path) -> str:
        """Read main.bicep content."""
        return main_bicep_path.read_text()

    def test_main_deploys_ai_foundry(self, main_bicep_content: str):
        """Test that main.bicep deploys AI Foundry module."""
        assert "modules/ai-foundry.bicep" in main_bicep_content, \
            "main.bicep should reference modules/ai-foundry.bicep"

    def test_no_old_foundry_hub_module(self, main_bicep_content: str):
        """Test that main.bicep does not use old hub module."""
        assert "ai-foundry-hub.bicep" not in main_bicep_content, \
            "main.bicep should not reference old ai-foundry-hub.bicep"

    def test_no_old_foundry_project_module(self, main_bicep_content: str):
        """Test that main.bicep does not use old project module."""
        assert "ai-foundry-project.bicep" not in main_bicep_content, \
            "main.bicep should not reference old ai-foundry-project.bicep"

    def test_no_old_foundry_connection_module(self, main_bicep_content: str):
        """Test that main.bicep does not use old connection module."""
        assert "ai-foundry-connection.bicep" not in main_bicep_content, \
            "main.bicep should not reference old ai-foundry-connection.bicep"

    def test_main_outputs_foundry_name(self, main_bicep_content: str):
        """Test that main.bicep outputs aiFoundryName."""
        assert re.search(r"output\s+aiFoundryName\s+string", main_bicep_content), \
            "main.bicep should output aiFoundryName"

    def test_main_outputs_foundry_project_name(self, main_bicep_content: str):
        """Test that main.bicep outputs aiFoundryProjectName."""
        assert re.search(r"output\s+aiFoundryProjectName\s+string", main_bicep_content), \
            "main.bicep should output aiFoundryProjectName"

    def test_main_outputs_foundry_endpoint(self, main_bicep_content: str):
        """Test that main.bicep outputs aiFoundryEndpoint."""
        assert re.search(r"output\s+aiFoundryEndpoint\s+string", main_bicep_content), \
            "main.bicep should output aiFoundryEndpoint"

    def test_backend_uses_foundry_outputs(self, main_bicep_content: str):
        """Test that backend container app uses AI Foundry outputs."""
        assert "aiFoundry.outputs.endpoint" in main_bicep_content, \
            "Backend should use aiFoundry.outputs.endpoint"
        assert "aiFoundry.outputs.deploymentName" in main_bicep_content, \
            "Backend should use aiFoundry.outputs.deploymentName"

    def test_backend_no_api_key_from_foundry(self, main_bicep_content: str):
        """Test that backend does not use API key from AI Foundry."""
        assert "aiFoundry.outputs.key" not in main_bicep_content, \
            "Backend should not use aiFoundry.outputs.key (managed identity)"


class TestManagedIdentity:
    """Tests for managed identity configuration in main.bicep."""

    @pytest.fixture
    def main_bicep_path(self) -> Path:
        """Path to main.bicep file."""
        return Path(__file__).parent.parent.parent / "infra" / "main.bicep"

    @pytest.fixture
    def main_bicep_content(self, main_bicep_path: Path) -> str:
        """Read main.bicep content."""
        return main_bicep_path.read_text()

    def test_has_user_assigned_identity(self, main_bicep_content: str):
        """Test that main.bicep creates a user-assigned managed identity."""
        assert "Microsoft.ManagedIdentity/userAssignedIdentities" \
            in main_bicep_content, \
            "main.bicep should create a user-assigned managed identity"

    def test_has_acr_pull_role_assignment(self, main_bicep_content: str):
        """Test that main.bicep assigns AcrPull role."""
        assert "7f951dda-4ed3-4680-a7ca-43fe172d538d" in main_bicep_content, \
            "main.bicep should have AcrPull role definition ID"
        assert "Microsoft.Authorization/roleAssignments" in main_bicep_content, \
            "main.bicep should have role assignments"

    def test_has_cognitive_services_role_assignment(
        self, main_bicep_content: str
    ):
        """Test that backend gets Cognitive Services OpenAI User role."""
        assert "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd" in main_bicep_content, \
            "main.bicep should have Cognitive Services OpenAI User role ID"

    def test_no_registry_credentials(self, main_bicep_content: str):
        """Test that no registry credentials are passed to container apps."""
        assert "registryUsername" not in main_bicep_content, \
            "main.bicep should not pass registryUsername"
        assert "registryPassword" not in main_bicep_content, \
            "main.bicep should not pass registryPassword"
        assert "adminUsername" not in main_bicep_content, \
            "main.bicep should not reference adminUsername"
        assert "adminPassword" not in main_bicep_content, \
            "main.bicep should not reference adminPassword"

    def test_no_api_key_secret(self, main_bicep_content: str):
        """Test that no API key secrets are configured."""
        assert "azure-openai-api-key" not in main_bicep_content, \
            "main.bicep should not have azure-openai-api-key secret"

    def test_passes_identity_to_container_apps(
        self, main_bicep_content: str
    ):
        """Test that userAssignedIdentityId is passed to container apps."""
        assert "userAssignedIdentityId:" in main_bicep_content, \
            "main.bicep should pass userAssignedIdentityId to container apps"

    def test_backend_depends_on_acr_role(self, main_bicep_content: str):
        """Test that backend depends on AcrPull role assignment."""
        assert re.search(
            r"backend.*dependsOn.*acrPullRoleAssignment",
            main_bicep_content, re.DOTALL
        ), "Backend should depend on acrPullRoleAssignment"

    def test_role_assignment_scoping(self, main_bicep_content: str):
        """Test that role assignments are scoped to specific resources."""
        assert "scope:" in main_bicep_content, \
            "Role assignments should be scoped to specific resources"
        assert "principalType: 'ServicePrincipal'" in main_bicep_content, \
            "Role assignments should specify principalType"


class TestParameterFiles:
    """Tests for Bicep parameter files."""

    @pytest.fixture
    def dev_param_path(self) -> Path:
        """Path to dev.bicepparam file."""
        return Path(__file__).parent.parent.parent / "infra" / "parameters" / "dev.bicepparam"

    @pytest.fixture
    def prod_param_path(self) -> Path:
        """Path to prod.bicepparam file."""
        return Path(__file__).parent.parent.parent / "infra" / "parameters" / "prod.bicepparam"

    @pytest.fixture
    def dev_param_content(self, dev_param_path: Path) -> str:
        """Read dev.bicepparam content."""
        return dev_param_path.read_text()

    @pytest.fixture
    def prod_param_content(self, prod_param_path: Path) -> str:
        """Read prod.bicepparam content."""
        return prod_param_path.read_text()

    def test_dev_param_exists(self, dev_param_path: Path):
        """Test that dev.bicepparam exists."""
        assert dev_param_path.exists(), "dev.bicepparam does not exist"
        assert dev_param_path.stat().st_size > 0, "dev.bicepparam is empty"

    def test_prod_param_exists(self, prod_param_path: Path):
        """Test that prod.bicepparam exists."""
        assert prod_param_path.exists(), "prod.bicepparam does not exist"
        assert prod_param_path.stat().st_size > 0, "prod.bicepparam is empty"

    def test_dev_references_main_bicep(self, dev_param_content: str):
        """Test that dev.bicepparam references main.bicep."""
        assert "main.bicep" in dev_param_content, \
            "dev.bicepparam should reference main.bicep"

    def test_prod_references_main_bicep(self, prod_param_content: str):
        """Test that prod.bicepparam references main.bicep."""
        assert "main.bicep" in prod_param_content, \
            "prod.bicepparam should reference main.bicep"

    def test_dev_uses_dev_environment(self, dev_param_content: str):
        """Test that dev.bicepparam uses environmentName = 'dev'."""
        assert re.search(r"environmentName\s*=\s*['\"]dev['\"]", dev_param_content), \
            "dev.bicepparam should set environmentName = 'dev'"

    def test_prod_uses_prod_environment(self, prod_param_content: str):
        """Test that prod.bicepparam uses environmentName = 'prod'."""
        assert re.search(r"environmentName\s*=\s*['\"]prod['\"]", prod_param_content), \
            "prod.bicepparam should set environmentName = 'prod'"


class TestEnvironmentsConfig:
    """Tests for the environments.json configuration file."""

    @pytest.fixture
    def config_path(self) -> Path:
        """Path to environments.json."""
        return Path(__file__).parent.parent.parent / "infra" / "environments.json"

    @pytest.fixture
    def config(self, config_path: Path) -> dict:
        """Read and parse environments.json."""
        import json
        return json.loads(config_path.read_text())

    def test_environments_json_exists(self, config_path: Path):
        """Test that environments.json exists."""
        assert config_path.exists(), "infra/environments.json does not exist"

    def test_has_dev_environment(self, config: dict):
        """Test that config has a dev environment."""
        assert "dev" in config, "environments.json should have a 'dev' entry"

    def test_has_prod_environment(self, config: dict):
        """Test that config has a prod environment."""
        assert "prod" in config, "environments.json should have a 'prod' entry"

    def test_dev_has_resource_group_name(self, config: dict):
        """Test that dev config has resourceGroupName."""
        assert "resourceGroupName" in config["dev"], \
            "dev config should have resourceGroupName"

    def test_prod_has_resource_group_name(self, config: dict):
        """Test that prod config has resourceGroupName."""
        assert "resourceGroupName" in config["prod"], \
            "prod config should have resourceGroupName"

    def test_dev_has_location(self, config: dict):
        """Test that dev config has location."""
        assert "location" in config["dev"], \
            "dev config should have location"

    def test_dev_resource_group_contains_dev(self, config: dict):
        """Test that dev resource group name contains 'dev'."""
        assert "dev" in config["dev"]["resourceGroupName"], \
            "dev resourceGroupName should contain 'dev'"

    def test_prod_resource_group_contains_prod(self, config: dict):
        """Test that prod resource group name contains 'prod'."""
        assert "prod" in config["prod"]["resourceGroupName"], \
            "prod resourceGroupName should contain 'prod'"
