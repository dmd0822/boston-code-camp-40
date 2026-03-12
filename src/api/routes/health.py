"""Health check endpoint.

Used by infrastructure probes (Container Apps liveness)
and developer sanity checks.
"""

from fastapi import APIRouter

from src.config.settings import get_settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return service health status and version.

    Returns:
        dict: ``{"status": "healthy", "version": "<ver>"}``
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
