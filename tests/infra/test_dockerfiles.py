"""
Validation tests for Dockerfiles and nginx configuration.

These tests validate that the Docker infrastructure is correctly configured
for production deployment.
"""

from pathlib import Path
import re
import pytest


class TestBackendDockerfile:
    """Tests for the backend Dockerfile."""

    @pytest.fixture
    def dockerfile_path(self) -> Path:
        """Path to the backend Dockerfile."""
        return Path(__file__).parent.parent.parent / "Dockerfile"

    @pytest.fixture
    def dockerfile_content(self, dockerfile_path: Path) -> str:
        """Read the backend Dockerfile content."""
        return dockerfile_path.read_text()

    def test_dockerfile_exists(self, dockerfile_path: Path):
        """Test that the backend Dockerfile exists and is not empty."""
        assert dockerfile_path.exists(), "Backend Dockerfile does not exist"
        assert dockerfile_path.stat().st_size > 0, "Backend Dockerfile is empty"

    def test_uses_python_312_slim(self, dockerfile_content: str):
        """Test that Dockerfile uses python:3.12-slim base image."""
        assert "python:3.12-slim" in dockerfile_content, \
            "Dockerfile should use python:3.12-slim base image"

    def test_exposes_port_8000(self, dockerfile_content: str):
        """Test that Dockerfile exposes port 8000."""
        assert "EXPOSE 8000" in dockerfile_content, \
            "Dockerfile should expose port 8000"

    def test_workdir_is_set(self, dockerfile_content: str):
        """Test that WORKDIR is set."""
        assert re.search(r'WORKDIR\s+/app', dockerfile_content), \
            "Dockerfile should set WORKDIR to /app"

    def test_copies_requirements_txt(self, dockerfile_content: str):
        """Test that requirements.txt is copied."""
        assert re.search(r'COPY\s+requirements\.txt', dockerfile_content), \
            "Dockerfile should copy requirements.txt"

    def test_copies_src_directory(self, dockerfile_content: str):
        """Test that src/ directory is copied."""
        assert re.search(r'COPY\s+src/', dockerfile_content), \
            "Dockerfile should copy src/ directory"

    def test_copies_entrypoints_directory(self, dockerfile_content: str):
        """Test that entrypoints/ directory is copied."""
        assert re.search(r'COPY\s+entrypoints/', dockerfile_content), \
            "Dockerfile should copy entrypoints/ directory"

    def test_copies_data_directory(self, dockerfile_content: str):
        """Test that data/ directory is copied."""
        assert re.search(r'COPY\s+data/', dockerfile_content), \
            "Dockerfile should copy data/ directory"

    def test_cmd_no_reload(self, dockerfile_content: str):
        """Test that CMD does not include --reload (production safety)."""
        # Find the CMD line
        cmd_match = re.search(r'CMD\s+\[.*?\]', dockerfile_content)
        assert cmd_match, "Dockerfile should have a CMD instruction"
        cmd_line = cmd_match.group(0)
        assert "--reload" not in cmd_line, \
            "Production CMD should not include --reload flag"

    def test_cmd_includes_workers(self, dockerfile_content: str):
        """Test that CMD includes --workers for production."""
        # Find the CMD line
        cmd_match = re.search(r'CMD\s+\[.*?\]', dockerfile_content)
        assert cmd_match, "Dockerfile should have a CMD instruction"
        cmd_line = cmd_match.group(0)
        assert "--workers" in cmd_line, \
            "Production CMD should include --workers flag"

    def test_does_not_copy_tests(self, dockerfile_content: str):
        """Test that tests/ directory is not copied."""
        assert not re.search(r'COPY\s+tests/', dockerfile_content), \
            "Dockerfile should not copy tests/ directory"

    def test_does_not_copy_notebooks(self, dockerfile_content: str):
        """Test that notebooks/ directory is not copied."""
        assert not re.search(r'COPY\s+notebooks/', dockerfile_content), \
            "Dockerfile should not copy notebooks/ directory"

    def test_does_not_copy_frontend(self, dockerfile_content: str):
        """Test that frontend/ directory is not copied."""
        assert not re.search(r'COPY\s+frontend/', dockerfile_content), \
            "Dockerfile should not copy frontend/ directory"

    def test_does_not_copy_env_file(self, dockerfile_content: str):
        """Test that .env file is not copied."""
        assert not re.search(r'COPY\s+\.env', dockerfile_content), \
            "Dockerfile should not copy .env file"


class TestFrontendDockerfile:
    """Tests for the frontend Dockerfile."""

    @pytest.fixture
    def dockerfile_path(self) -> Path:
        """Path to the frontend Dockerfile."""
        return Path(__file__).parent.parent.parent / "frontend" / "Dockerfile"

    @pytest.fixture
    def dockerfile_content(self, dockerfile_path: Path) -> str:
        """Read the frontend Dockerfile content."""
        return dockerfile_path.read_text()

    def test_dockerfile_exists(self, dockerfile_path: Path):
        """Test that the frontend Dockerfile exists."""
        assert dockerfile_path.exists(), "Frontend Dockerfile does not exist"
        assert dockerfile_path.stat().st_size > 0, "Frontend Dockerfile is empty"

    def test_multi_stage_build(self, dockerfile_content: str):
        """Test that Dockerfile has multi-stage build (multiple FROM statements)."""
        from_count = len(re.findall(r'^FROM\s+', dockerfile_content, re.MULTILINE))
        assert from_count >= 2, \
            "Frontend Dockerfile should have multi-stage build (at least 2 FROM statements)"

    def test_build_stage_uses_node(self, dockerfile_content: str):
        """Test that build stage uses node image."""
        assert re.search(r'FROM\s+node:', dockerfile_content), \
            "Build stage should use node image"

    def test_production_stage_uses_nginx(self, dockerfile_content: str):
        """Test that production stage uses nginx image."""
        assert re.search(r'FROM\s+nginx:', dockerfile_content), \
            "Production stage should use nginx image"

    def test_runs_npm_ci(self, dockerfile_content: str):
        """Test that Dockerfile runs npm ci."""
        assert "npm ci" in dockerfile_content, \
            "Dockerfile should run npm ci for reproducible builds"

    def test_runs_npm_build(self, dockerfile_content: str):
        """Test that Dockerfile runs npm run build."""
        assert "npm run build" in dockerfile_content, \
            "Dockerfile should run npm run build"

    def test_exposes_port_80(self, dockerfile_content: str):
        """Test that Dockerfile exposes port 80."""
        assert "EXPOSE 80" in dockerfile_content, \
            "Frontend Dockerfile should expose port 80"

    def test_copies_nginx_conf(self, dockerfile_content: str):
        """Test that nginx.conf.template is copied."""
        assert re.search(
            r'COPY\s+.*nginx\.conf\.template', dockerfile_content
        ), "Dockerfile should copy nginx.conf.template"


class TestNginxConfig:
    """Tests for the nginx configuration."""

    @pytest.fixture
    def nginx_conf_path(self) -> Path:
        """Path to the nginx configuration template."""
        return Path(__file__).parent.parent.parent / "frontend" / "nginx.conf.template"

    @pytest.fixture
    def nginx_conf_content(self, nginx_conf_path: Path) -> str:
        """Read the nginx configuration template content."""
        return nginx_conf_path.read_text()

    def test_nginx_conf_exists(self, nginx_conf_path: Path):
        """Test that nginx.conf.template exists."""
        assert nginx_conf_path.exists(), "nginx.conf.template does not exist"
        assert nginx_conf_path.stat().st_size > 0, "nginx.conf.template is empty"

    def test_has_proxy_pass_for_api(self, nginx_conf_content: str):
        """Test that nginx.conf contains proxy_pass directive for /api."""
        assert "location /api/" in nginx_conf_content, \
            "nginx.conf should have location block for /api/"
        assert "proxy_pass" in nginx_conf_content, \
            "nginx.conf should have proxy_pass directive for API requests"

    def test_has_spa_fallback(self, nginx_conf_content: str):
        """Test that nginx.conf has try_files for SPA fallback."""
        assert "try_files" in nginx_conf_content, \
            "nginx.conf should have try_files for SPA routing"
        assert re.search(r'try_files.*index\.html', nginx_conf_content), \
            "nginx.conf should fallback to index.html for SPA routes"

    def test_has_gzip_configuration(self, nginx_conf_content: str):
        """Test that nginx.conf has gzip compression enabled."""
        assert "gzip on" in nginx_conf_content, \
            "nginx.conf should enable gzip compression"
        assert "gzip_types" in nginx_conf_content, \
            "nginx.conf should specify gzip types"
