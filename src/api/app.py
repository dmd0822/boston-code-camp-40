"""FastAPI application factory.

Creates and configures the FastAPI app with CORS middleware
and route registration. Kept as a factory function so tests
can create isolated app instances.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, itinerary
from src.config.settings import get_settings


def create_app() -> FastAPI:
    """Build the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="Travel Agent API",
        description=(
            "AI-powered travel itinerary generator using "
            "Microsoft Agent Framework"
        ),
        version=settings.APP_VERSION,
    )

    # CORS — permissive for MVP (no auth)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register route modules
    app.include_router(health.router)
    app.include_router(itinerary.router)

    return app
