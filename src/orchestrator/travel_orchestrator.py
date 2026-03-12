"""Travel orchestrator — coordinates agent pipeline.

Phase 1 (Sequential): General Agent recommends destinations.
Phase 2 (Concurrent): POI/Event/Weather agents enrich each dest.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, List, Optional, TypeVar

from src.agents.event_agent import find_events
from src.agents.general_agent import recommend_destinations
from src.agents.poi_agent import find_points_of_interest
from src.agents.weather_agent import get_weather_forecast
from src.api.models.customer import CustomerProfile, TravelDates
from src.api.models.itinerary import (
    Destination,
    Event,
    ItineraryResponse,
    PointOfInterest,
    WeatherForecast,
)
from src.config.settings import Settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TravelOrchestrator:
    """Orchestrates the agent pipeline for itinerary generation.

    Two-phase execution:
    1. Sequential: General Agent recommends 3-4 destinations
    2. Concurrent: POI/Event/Weather agents enrich each destination

    Error handling: Specialist agent failures result in partial
    data (empty lists, None) rather than cascading failures.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the orchestrator with configuration.

        Args:
            settings: Application settings for agent initialization.
        """
        self.settings = settings

    async def generate_itinerary(
        self, profile: CustomerProfile
    ) -> ItineraryResponse:
        """Build an itinerary for the given customer profile.

        Args:
            profile: Validated customer preferences and constraints.

        Returns:
            ItineraryResponse with enriched destinations.
        """
        # Phase 1: Get destinations from General Agent (sequential)
        try:
            destinations = await recommend_destinations(
                profile, self.settings
            )
        except Exception as exc:
            logger.error(
                f"General Agent failed: {exc}",
                exc_info=True,
            )
            # Return empty itinerary on General Agent failure
            return ItineraryResponse(
                destinations=[],
                generated_at=datetime.now(timezone.utc),
            )

        if not destinations:
            logger.info("General Agent returned no destinations")
            return ItineraryResponse(
                destinations=[],
                generated_at=datetime.now(timezone.utc),
            )

        # Phase 2: Enrich destinations concurrently
        enriched_destinations = await asyncio.gather(
            *[
                self._enrich_destination(dest, profile.travel_dates)
                for dest in destinations
            ]
        )

        return ItineraryResponse(
            destinations=enriched_destinations,
            generated_at=datetime.now(timezone.utc),
        )

    async def _enrich_destination(
        self, destination: Destination, travel_dates: TravelDates
    ) -> Destination:
        """Enrich a destination with POI, event, and weather data.

        Uses concurrent execution to fan-out to specialist agents,
        then merges results back into the destination.

        Args:
            destination: Base destination from General Agent.
            travel_dates: Customer travel date range.

        Returns:
            Enriched destination with POI, events, and weather.
        """
        # Fan-out: Call all specialist agents concurrently
        poi_task = self._safe_call(
            find_points_of_interest,
            destination.name,
            destination.country,
            travel_dates,
            self.settings,
            default=[],
        )
        event_task = self._safe_call(
            find_events,
            destination.name,
            destination.country,
            travel_dates,
            self.settings,
            default=[],
        )
        weather_task = self._safe_call(
            get_weather_forecast,
            destination.name,
            destination.country,
            travel_dates,
            self.settings,
            default=None,
        )

        poi_list, event_list, weather = await asyncio.gather(
            poi_task, event_task, weather_task
        )

        # Fan-in: Merge results into destination
        destination.points_of_interest = poi_list
        destination.events = event_list
        destination.weather = weather

        return destination

    async def _safe_call(
        self,
        agent_func: Callable[..., T],
        *args,
        default: T,
        **kwargs,
    ) -> T:
        """Wrap agent call with error handling and default fallback.

        Args:
            agent_func: The agent function to call.
            *args: Positional arguments for the agent function.
            default: Default value to return on failure.
            **kwargs: Keyword arguments for the agent function.

        Returns:
            Agent function result on success, default on failure.
        """
        try:
            return await agent_func(*args, **kwargs)
        except Exception as exc:
            logger.warning(
                f"Agent {agent_func.__name__} failed: {exc}. "
                f"Using default: {default}"
            )
            return default
