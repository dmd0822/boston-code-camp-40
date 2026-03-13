"""Itinerary generation endpoint.

Accepts a CustomerProfile and returns an ItineraryResponse.
Orchestrates the full agent pipeline: General Agent for
destinations, then POI/Event/Weather agents for enrichment.
"""

import logging

from fastapi import APIRouter, Depends
from pydantic import ValidationError

from src.api.error_handlers import ErrorResponse
from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import ItineraryResponse
from src.config.settings import Settings, get_settings
from src.exceptions import (
    ExternalServiceError,
    ExternalServiceTimeoutError,
    ItineraryGenerationError,
    ServiceConfigurationError,
)
from src.orchestrator.travel_orchestrator import TravelOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["itinerary"])
ERROR_RESPONSES = {
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
    502: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
    504: {"model": ErrorResponse},
}


def get_route_settings() -> Settings:
    """Load request settings with a stable configuration error.

    Returns:
        Settings: Application settings for the current process.

    Raises:
        ServiceConfigurationError: If the application settings are
            invalid.
    """
    try:
        return get_settings()
    except ValidationError as exc:
        logger.error(
            "Application settings failed validation.",
            exc_info=True,
        )
        raise ServiceConfigurationError(
            "Application settings are invalid or incomplete."
        ) from exc


@router.post(
    "/itinerary",
    response_model=ItineraryResponse,
    responses=ERROR_RESPONSES,
)
async def generate_itinerary(
    profile: CustomerProfile,
    settings: Settings = Depends(get_route_settings),
) -> ItineraryResponse:
    """Generate a travel itinerary from a customer profile.

    Args:
        profile: Customer preferences and constraints.
        settings: Application settings injected by FastAPI.

    Returns:
        ItineraryResponse with enriched destinations.

    Raises:
        ServiceConfigurationError: If required backend config is
            missing.
        ExternalServiceTimeoutError: If Azure OpenAI times out.
        ExternalServiceError: If an upstream AI dependency fails.
        ItineraryGenerationError: If generation fails unexpectedly.
    """
    logger.info(
        "Generating itinerary for departure city '%s'.",
        profile.departure_city,
    )

    orchestrator = TravelOrchestrator(settings)
    try:
        return await orchestrator.generate_itinerary(profile)
    except (
        ExternalServiceTimeoutError,
        ServiceConfigurationError,
        ExternalServiceError,
        ItineraryGenerationError,
    ):
        raise
    except TimeoutError as exc:
        logger.error(
            "Itinerary generation timed out unexpectedly.",
            exc_info=True,
        )
        raise ExternalServiceTimeoutError(
            "The itinerary request timed out."
        ) from exc
    except (RuntimeError, TypeError, ValueError) as exc:
        logger.error(
            "Itinerary generation failed unexpectedly.",
            exc_info=True,
        )
        raise ItineraryGenerationError(
            "The itinerary could not be generated at this time."
        ) from exc
