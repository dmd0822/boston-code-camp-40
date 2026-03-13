"""
Integration tests for Docker build process.

These tests actually build the Docker images to verify that the
Dockerfiles are valid and can successfully create images.

These tests are marked as 'slow' and require Docker to be installed.
"""

from pathlib import Path
import subprocess
import pytest
import shutil


def is_docker_available() -> bool:
    """Check if Docker is installed and the daemon is running."""
    if shutil.which("docker") is None:
        return False
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


@pytest.mark.slow
@pytest.mark.skipif(not is_docker_available(), reason="Docker is not available")
class TestDockerBuild:
    """Integration tests for Docker image building."""

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root path."""
        return Path(__file__).parent.parent.parent

    def test_backend_docker_build(self, repo_root: Path):
        """
        Test that the backend Dockerfile builds successfully.
        
        This test runs: docker build -t travel-agent-backend-test .
        """
        result = subprocess.run(
            ["docker", "build", "-t", "travel-agent-backend-test", "."],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        assert result.returncode == 0, \
            f"Backend Docker build failed:\n{result.stdout}\n{result.stderr}"

    def test_frontend_docker_build(self, repo_root: Path):
        """
        Test that the frontend Dockerfile builds successfully.
        
        This test runs: docker build -t travel-agent-frontend-test src/frontend/
        """
        result = subprocess.run(
            ["docker", "build", "-t", "travel-agent-frontend-test", "src/frontend"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        assert result.returncode == 0, \
            f"Frontend Docker build failed:\n{result.stdout}\n{result.stderr}"

    def test_backend_image_created(self):
        """Test that the backend image was created and exists."""
        result = subprocess.run(
            ["docker", "images", "-q", "travel-agent-backend-test"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Failed to check for backend image"
        assert result.stdout.strip(), "Backend image was not created"

    def test_frontend_image_created(self):
        """Test that the frontend image was created and exists."""
        result = subprocess.run(
            ["docker", "images", "-q", "travel-agent-frontend-test"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Failed to check for frontend image"
        assert result.stdout.strip(), "Frontend image was not created"
