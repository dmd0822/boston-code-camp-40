"""Itinerary generation endpoint.

Accepts a CustomerProfile and returns an ItineraryResponse.
Orchestrates the full agent pipeline: General Agent for
destinations, then POI/Event/Weather agents for enrichment.
"""

from fastapi import APIRouter, Depends

from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import ItineraryResponse
from src.config.settings import Settings, get_settings
from src.orchestrator.travel_orchestrator import (
    TravelOrchestrator,
)

router = APIRouter(prefix="/api", tags=["itinerary"])


@router.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(
    profile: CustomerProfile,
    settings: Settings = Depends(get_settings),
) -> ItineraryResponse:
    """Generate a travel itinerary from a customer profile.

    Args:
        profile: Customer preferences and constraints.
        settings: Application settings injected by FastAPI.

    Returns:
        ItineraryResponse with enriched destinations.
    """
    orchestrator = TravelOrchestrator(settings)
    return await orchestrator.generate_itinerary(profile)
