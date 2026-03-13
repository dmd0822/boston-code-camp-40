"""FastAPI application factory.

Creates and configures the FastAPI app with CORS middleware
and route registration. Kept as a factory function so tests
can create isolated app instances.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.error_handlers import register_exception_handlers
from src.api.routes import health, itinerary
from src.config.settings import get_settings

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def _configure_logging(log_level: str) -> None:
    """Configure root logging for the backend application.

    Args:
        log_level: Logging level name such as ``INFO`` or ``DEBUG``.
    """
    resolved_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(level=resolved_level, format=LOG_FORMAT)

    root_logger.setLevel(resolved_level)


def create_app() -> FastAPI:
    """Build the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    settings = get_settings()
    _configure_logging(settings.LOG_LEVEL)

    app = FastAPI(
        title="Travel Agent API",
        description=(
            "AI-powered travel itinerary generator using "
            "Microsoft Agent Framework"
        ),
        version=settings.APP_VERSION,
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(itinerary.router)

    return app
