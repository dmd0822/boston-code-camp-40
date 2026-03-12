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

    def test_target_scope_is_subscription(self, main_bicep_content: str):
        """Test that main.bicep targets subscription scope."""
        assert re.search(r"targetScope\s*=\s*'subscription'", main_bicep_content), \
            "main.bicep should have targetScope = 'subscription'"

    def test_has_resource_group_name_parameter(self, main_bicep_content: str):
        """Test that main.bicep has resourceGroupName parameter."""
        assert re.search(r"param\s+resourceGroupName\s+string", main_bicep_content), \
            "main.bicep should have resourceGroupName parameter"

    def test_resource_group_default_naming(self, main_bicep_content: str):
        """Test that resourceGroupName defaults to rg-travel-agent-{env}."""
        assert re.search(
            r"param\s+resourceGroupName\s+string\s*=\s*'rg-travel-agent-\$\{environmentName\}'",
            main_bicep_content
        ), "resourceGroupName should default to 'rg-travel-agent-${environmentName}'"

    def test_creates_resource_group(self, main_bicep_content: str):
        """Test that main.bicep creates a resource group resource."""
        assert re.search(
            r"resource\s+\w+\s+'Microsoft\.Resources/resourceGroups@",
            main_bicep_content
        ), "main.bicep should create a Microsoft.Resources/resourceGroups resource"

    def test_modules_scoped_to_resource_group(self, main_bicep_content: str):
        """Test that modules are scoped to the resource group."""
        assert "scope: rg" in main_bicep_content, \
            "Modules should be scoped to the resource group"

    def test_outputs_resource_group_name(self, main_bicep_content: str):
        """Test that main.bicep outputs the resource group name."""
        assert re.search(r"output\s+resourceGroupName\s+string", main_bicep_content), \
            "main.bicep should output resourceGroupName"

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

    def test_references_openai_module(self, main_bicep_content: str):
        """Test that main.bicep references openai.bicep module."""
        assert "modules/openai.bicep" in main_bicep_content, \
            "main.bicep should reference modules/openai.bicep"

    def test_references_bing_search_module(self, main_bicep_content: str):
        """Test that main.bicep references bing-search.bicep module."""
        assert "modules/bing-search.bicep" in main_bicep_content, \
            "main.bicep should reference modules/bing-search.bicep"

    def test_passes_azure_openai_endpoint(self, main_bicep_content: str):
        """Test that AZURE_OPENAI_ENDPOINT is passed to backend."""
        assert re.search(r"name:\s*['\"]AZURE_OPENAI_ENDPOINT['\"]", main_bicep_content), \
            "main.bicep should pass AZURE_OPENAI_ENDPOINT to backend"

    def test_passes_azure_openai_api_key(self, main_bicep_content: str):
        """Test that AZURE_OPENAI_API_KEY is passed to backend."""
        assert re.search(r"name:\s*['\"]AZURE_OPENAI_API_KEY['\"]", main_bicep_content), \
            "main.bicep should pass AZURE_OPENAI_API_KEY to backend"

    def test_passes_azure_openai_deployment(self, main_bicep_content: str):
        """Test that AZURE_OPENAI_DEPLOYMENT is passed to backend."""
        assert re.search(r"name:\s*['\"]AZURE_OPENAI_DEPLOYMENT['\"]", main_bicep_content), \
            "main.bicep should pass AZURE_OPENAI_DEPLOYMENT to backend"

    def test_passes_bing_search_api_key(self, main_bicep_content: str):
        """Test that BING_SEARCH_API_KEY is passed to backend."""
        assert re.search(r"name:\s*['\"]BING_SEARCH_API_KEY['\"]", main_bicep_content), \
            "main.bicep should pass BING_SEARCH_API_KEY to backend"

    def test_passes_bing_search_endpoint(self, main_bicep_content: str):
        """Test that BING_SEARCH_ENDPOINT is passed to backend."""
        assert re.search(r"name:\s*['\"]BING_SEARCH_ENDPOINT['\"]", main_bicep_content), \
            "main.bicep should pass BING_SEARCH_ENDPOINT to backend"

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

    def test_has_admin_user_enabled(self, module_content: str):
        """Test that adminUserEnabled is configured."""
        assert "adminUserEnabled" in module_content, \
            "Module should configure adminUserEnabled"

    def test_has_output_declarations(self, module_content: str):
        """Test that module has output declarations."""
        assert re.search(r"output\s+\w+", module_content), \
            "Module should have output declarations"


class TestOpenAIModule:
    """Tests for the openai.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to openai.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "openai.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_module_exists(self, module_path: Path):
        """Test that openai.bicep exists."""
        assert module_path.exists(), "openai.bicep does not exist"
        assert module_path.stat().st_size > 0, "openai.bicep is empty"

    def test_has_description_decorators(self, module_content: str):
        """Test that parameters have @description decorators."""
        assert "@description(" in module_content, \
            "Module should have @description decorators on parameters"

    def test_creates_cognitive_services_account(self, module_content: str):
        """Test that module creates Microsoft.CognitiveServices/accounts resource."""
        assert "Microsoft.CognitiveServices/accounts" in module_content, \
            "Module should create Microsoft.CognitiveServices/accounts resource"

    def test_has_model_deployment(self, module_content: str):
        """Test that module has model deployment configuration."""
        assert "deployments" in module_content or "deployment" in module_content, \
            "Module should configure model deployment"

    def test_has_output_declarations(self, module_content: str):
        """Test that module has output declarations."""
        assert re.search(r"output\s+\w+", module_content), \
            "Module should have output declarations"


class TestBingSearchModule:
    """Tests for the bing-search.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to bing-search.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "bing-search.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_module_exists(self, module_path: Path):
        """Test that bing-search.bicep exists."""
        assert module_path.exists(), "bing-search.bicep does not exist"
        assert module_path.stat().st_size > 0, "bing-search.bicep is empty"

    def test_has_description_decorators(self, module_content: str):
        """Test that parameters have @description decorators."""
        assert "@description(" in module_content, \
            "Module should have @description decorators on parameters"

    def test_creates_bing_account(self, module_content: str):
        """Test that module creates Microsoft.Bing/accounts resource."""
        assert "Microsoft.Bing/accounts" in module_content, \
            "Module should create Microsoft.Bing/accounts resource"

    def test_location_is_global(self, module_content: str):
        """Test that location is set to 'global' for Bing Search."""
        assert re.search(r"location:\s*['\"]global['\"]", module_content), \
            "Bing Search location should be 'global'"

    def test_has_output_declarations(self, module_content: str):
        """Test that module has output declarations."""
        assert re.search(r"output\s+\w+", module_content), \
            "Module should have output declarations"


class TestAIFoundryHub:
    """Tests for the ai-foundry-hub.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to ai-foundry-hub.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "ai-foundry-hub.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_hub_module_exists(self, module_path: Path):
        """Test that ai-foundry-hub.bicep exists."""
        assert module_path.exists(), "ai-foundry-hub.bicep does not exist"
        assert module_path.stat().st_size > 0, "ai-foundry-hub.bicep is empty"

    def test_hub_has_name_param(self, module_content: str):
        """Test that module has name parameter."""
        assert re.search(r"param\s+name\s+string", module_content), \
            "Module should have name parameter"

    def test_hub_has_location_param(self, module_content: str):
        """Test that module has location parameter."""
        assert re.search(r"param\s+location\s+string", module_content), \
            "Module should have location parameter"

    def test_hub_resource_type(self, module_content: str):
        """Test that module uses Microsoft.MachineLearningServices/workspaces resource type."""
        assert "Microsoft.MachineLearningServices/workspaces" in module_content, \
            "Module should use Microsoft.MachineLearningServices/workspaces resource type"

    def test_hub_kind_is_hub(self, module_content: str):
        """Test that kind is 'Hub'."""
        assert re.search(r"kind:\s*['\"]Hub['\"]", module_content), \
            "Module should set kind: 'Hub'"

    def test_hub_has_system_identity(self, module_content: str):
        """Test that identity type is SystemAssigned."""
        assert re.search(r"type:\s*['\"]SystemAssigned['\"]", module_content), \
            "Module should have identity type: 'SystemAssigned'"

    def test_hub_outputs_id(self, module_content: str):
        """Test that module outputs id."""
        assert re.search(r"output\s+id\s+string", module_content), \
            "Module should output id"

    def test_hub_outputs_name(self, module_content: str):
        """Test that module outputs name."""
        assert re.search(r"output\s+name\s+string", module_content), \
            "Module should output name"

    def test_hub_outputs_principal_id(self, module_content: str):
        """Test that module outputs principalId."""
        assert re.search(r"output\s+principalId\s+string", module_content), \
            "Module should output principalId"


class TestAIFoundryProject:
    """Tests for the ai-foundry-project.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to ai-foundry-project.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "ai-foundry-project.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_project_module_exists(self, module_path: Path):
        """Test that ai-foundry-project.bicep exists."""
        assert module_path.exists(), "ai-foundry-project.bicep does not exist"
        assert module_path.stat().st_size > 0, "ai-foundry-project.bicep is empty"

    def test_project_has_name_param(self, module_content: str):
        """Test that module has name parameter."""
        assert re.search(r"param\s+name\s+string", module_content), \
            "Module should have name parameter"

    def test_project_has_hub_id_param(self, module_content: str):
        """Test that module has hubId parameter."""
        assert re.search(r"param\s+hubId\s+string", module_content), \
            "Module should have hubId parameter"

    def test_project_resource_type(self, module_content: str):
        """Test that module uses Microsoft.MachineLearningServices/workspaces resource type."""
        assert "Microsoft.MachineLearningServices/workspaces" in module_content, \
            "Module should use Microsoft.MachineLearningServices/workspaces resource type"

    def test_project_kind_is_project(self, module_content: str):
        """Test that kind is 'Project'."""
        assert re.search(r"kind:\s*['\"]Project['\"]", module_content), \
            "Module should set kind: 'Project'"

    def test_project_has_system_identity(self, module_content: str):
        """Test that identity type is SystemAssigned."""
        assert re.search(r"type:\s*['\"]SystemAssigned['\"]", module_content), \
            "Module should have identity type: 'SystemAssigned'"

    def test_project_links_to_hub(self, module_content: str):
        """Test that project links to hub via hubResourceId."""
        assert "hubResourceId" in module_content, \
            "Module should have hubResourceId in properties"

    def test_project_outputs_id(self, module_content: str):
        """Test that module outputs id."""
        assert re.search(r"output\s+id\s+string", module_content), \
            "Module should output id"

    def test_project_outputs_name(self, module_content: str):
        """Test that module outputs name."""
        assert re.search(r"output\s+name\s+string", module_content), \
            "Module should output name"


class TestAIFoundryConnection:
    """Tests for the ai-foundry-connection.bicep module."""

    @pytest.fixture
    def module_path(self) -> Path:
        """Path to ai-foundry-connection.bicep module."""
        return Path(__file__).parent.parent.parent / "infra" / "modules" / "ai-foundry-connection.bicep"

    @pytest.fixture
    def module_content(self, module_path: Path) -> str:
        """Read module content."""
        return module_path.read_text()

    def test_connection_module_exists(self, module_path: Path):
        """Test that ai-foundry-connection.bicep exists."""
        assert module_path.exists(), "ai-foundry-connection.bicep does not exist"
        assert module_path.stat().st_size > 0, "ai-foundry-connection.bicep is empty"

    def test_connection_has_hub_name_param(self, module_content: str):
        """Test that module has hubName parameter."""
        assert re.search(r"param\s+hubName\s+string", module_content), \
            "Module should have hubName parameter"

    def test_connection_has_openai_endpoint_param(self, module_content: str):
        """Test that module has openaiEndpoint parameter."""
        assert re.search(r"param\s+openaiEndpoint\s+string", module_content), \
            "Module should have openaiEndpoint parameter"

    def test_connection_has_secure_api_key(self, module_content: str):
        """Test that openaiApiKey parameter has @secure() decorator."""
        assert re.search(r"@secure\(\)\s*param\s+openaiApiKey\s+string", module_content, re.MULTILINE), \
            "Module should have @secure() decorator on openaiApiKey parameter"

    def test_connection_category_is_azure_openai(self, module_content: str):
        """Test that category is 'AzureOpenAI'."""
        assert re.search(r"category:\s*['\"]AzureOpenAI['\"]", module_content), \
            "Module should set category: 'AzureOpenAI'"

    def test_connection_auth_type(self, module_content: str):
        """Test that authType is 'ApiKey'."""
        assert re.search(r"authType:\s*['\"]ApiKey['\"]", module_content), \
            "Module should set authType: 'ApiKey'"

    def test_connection_is_shared(self, module_content: str):
        """Test that isSharedToAll is true."""
        assert re.search(r"isSharedToAll:\s*true", module_content), \
            "Module should set isSharedToAll: true"

    def test_connection_outputs_id(self, module_content: str):
        """Test that module outputs id."""
        assert re.search(r"output\s+id\s+string", module_content), \
            "Module should output id"


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

    def test_main_deploys_foundry_hub(self, main_bicep_content: str):
        """Test that main.bicep deploys AI Foundry Hub module."""
        assert "modules/ai-foundry-hub.bicep" in main_bicep_content, \
            "main.bicep should reference modules/ai-foundry-hub.bicep"

    def test_main_deploys_foundry_project(self, main_bicep_content: str):
        """Test that main.bicep deploys AI Foundry Project module."""
        assert "modules/ai-foundry-project.bicep" in main_bicep_content, \
            "main.bicep should reference modules/ai-foundry-project.bicep"

    def test_main_deploys_openai_connection(self, main_bicep_content: str):
        """Test that main.bicep deploys OpenAI connection module."""
        assert "modules/ai-foundry-connection.bicep" in main_bicep_content, \
            "main.bicep should reference modules/ai-foundry-connection.bicep"

    def test_main_hub_name_convention(self, main_bicep_content: str):
        """Test that hub uses baseName-ai-hub naming convention."""
        assert re.search(r"name:\s*['\"]?\$\{baseName\}-ai-hub['\"]?", main_bicep_content), \
            "main.bicep should use ${baseName}-ai-hub naming for hub"

    def test_main_project_depends_on_hub(self, main_bicep_content: str):
        """Test that project gets hubId from hub outputs."""
        assert re.search(r"hubId:\s*aiFoundryHub\.outputs\.id", main_bicep_content), \
            "main.bicep should pass aiFoundryHub.outputs.id to project"

    def test_main_connection_depends_on_hub(self, main_bicep_content: str):
        """Test that connection gets hubName from hub outputs."""
        assert re.search(r"hubName:\s*aiFoundryHub\.outputs\.name", main_bicep_content), \
            "main.bicep should pass aiFoundryHub.outputs.name to connection"

    def test_main_outputs_foundry_hub_name(self, main_bicep_content: str):
        """Test that main.bicep outputs foundryHubName."""
        assert re.search(r"output\s+foundryHubName\s+string", main_bicep_content), \
            "main.bicep should output foundryHubName"

    def test_main_outputs_foundry_project_name(self, main_bicep_content: str):
        """Test that main.bicep outputs foundryProjectName."""
        assert re.search(r"output\s+foundryProjectName\s+string", main_bicep_content), \
            "main.bicep should output foundryProjectName"


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

    def test_dev_has_resource_group_name(self, dev_param_content: str):
        """Test that dev.bicepparam sets resourceGroupName."""
        assert re.search(r"resourceGroupName\s*=", dev_param_content), \
            "dev.bicepparam should set resourceGroupName"

    def test_prod_has_resource_group_name(self, prod_param_content: str):
        """Test that prod.bicepparam sets resourceGroupName."""
        assert re.search(r"resourceGroupName\s*=", prod_param_content), \
            "prod.bicepparam should set resourceGroupName"

    def test_dev_resource_group_uses_dev(self, dev_param_content: str):
        """Test that dev resource group name contains 'dev'."""
        assert re.search(r"resourceGroupName\s*=\s*'[^']*dev[^']*'", dev_param_content), \
            "dev.bicepparam resourceGroupName should contain 'dev'"

    def test_prod_resource_group_uses_prod(self, prod_param_content: str):
        """Test that prod resource group name contains 'prod'."""
        assert re.search(r"resourceGroupName\s*=\s*'[^']*prod[^']*'", prod_param_content), \
            "prod.bicepparam resourceGroupName should contain 'prod'"
