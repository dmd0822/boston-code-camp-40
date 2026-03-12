"""Itinerary generation endpoint.

Accepts a CustomerProfile and returns an ItineraryResponse.
In Phase 1 the orchestrator returns mock data; in Phase 2 it
will invoke the real agent pipeline.
"""

from fastapi import APIRouter

from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import ItineraryResponse
from src.orchestrator.travel_orchestrator import (
    TravelOrchestrator,
)

router = APIRouter(prefix="/api", tags=["itinerary"])

# Single orchestrator instance — stateless, safe to reuse.
_orchestrator = TravelOrchestrator()


@router.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(
    profile: CustomerProfile,
) -> ItineraryResponse:
    """Generate a travel itinerary from a customer profile.

    Parameters:
        profile: Customer preferences and constraints.

    Returns:
        ItineraryResponse with enriched destinations.
    """
    return await _orchestrator.generate_itinerary(profile)
