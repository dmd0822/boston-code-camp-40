"""Health check endpoint.

Used by infrastructure probes (Container Apps liveness)
and developer sanity checks.
"""

from typing import Dict

from fastapi import APIRouter
from pydantic import ValidationError

from src.config.settings import get_settings
from src.exceptions import ServiceConfigurationError

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Return service health status and version.

    Returns:
        dict: ``{"status": "healthy", "version": "<ver>"}``

    Raises:
        ServiceConfigurationError: If the application settings fail to
            load.
    """
    try:
        settings = get_settings()
    except ValidationError as exc:
        raise ServiceConfigurationError(
            "Application settings could not be loaded."
        ) from exc

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
