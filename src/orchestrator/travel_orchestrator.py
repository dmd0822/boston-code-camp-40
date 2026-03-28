"""Travel orchestrator — coordinates agent pipeline.

Phase 1 (Sequential): General Agent recommends destinations.
Phase 2 (Concurrent): POI/Event/Weather/Travel Advisory agents
enrich each destination.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar

from azure.core.exceptions import AzureError

from src.agents.event_agent import find_events
from src.agents.general_agent import recommend_destinations
from src.agents.poi_agent import find_points_of_interest
from src.agents.travel_advisory_agent import get_travel_advisory
from src.agents.weather_agent import get_weather_forecast
from src.api.models.customer import CustomerProfile, TravelDates
from src.api.models.itinerary import (
    Destination,
    Event,
    ItineraryResponse,
    PointOfInterest,
    TravelAdvisory,
    WeatherForecast,
)
from src.config.settings import Settings
from src.exceptions import (
    ApplicationError,
    ItineraryGenerationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class AgentCallResult(Generic[T]):
    """Result wrapper that distinguishes success from fallback."""

    value: T
    failed: bool = False


class TravelOrchestrator:
    """Orchestrate the agent pipeline for itinerary generation.

    Two-phase execution:
    1. Sequential: General Agent recommends at least 3 destinations.
    2. Concurrent: POI/Event/Weather/Travel Advisory agents
       enrich each destination.

    Specialist agent failures degrade gracefully to partial results,
    while General Agent failures bubble up to the API layer.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the orchestrator with configuration.

        Args:
            settings: Application settings for agent initialization.
        """
        self.settings = settings

    async def generate_itinerary(
        self,
        profile: CustomerProfile,
    ) -> ItineraryResponse:
        """Build an itinerary for the given customer profile.

        Args:
            profile: Validated customer preferences and constraints.

        Returns:
            ItineraryResponse with enriched destinations.

        Raises:
            ApplicationError: If the General Agent cannot complete.
            ItineraryGenerationError: If orchestration fails.
        """
        try:
            destinations = await recommend_destinations(
                profile,
                self.settings,
            )
        except ApplicationError:
            logger.error(
                "General Agent failed to recommend destinations.",
                exc_info=True,
            )
            raise
        except (AzureError, RuntimeError, TimeoutError, TypeError) as exc:
            logger.error(
                "Destination recommendation failed unexpectedly.",
                exc_info=True,
            )
            raise ItineraryGenerationError(
                "The itinerary could not be generated."
            ) from exc
        except Exception as exc:
            logger.error(
                "Destination recommendation failed unexpectedly.",
                exc_info=True,
            )
            raise ItineraryGenerationError(
                "The itinerary could not be generated."
            ) from exc

        if not destinations:
            logger.info("General Agent returned no destinations.")
            return ItineraryResponse(
                destinations=[],
                generated_at=datetime.now(timezone.utc),
            )

        if len(destinations) < 3:
            logger.error(
                "General Agent returned only %s destinations (minimum "
                "3 required).",
                len(destinations),
            )
            raise ItineraryGenerationError(
                f"Only {len(destinations)} destinations were generated, "
                "but at least 3 are required for a complete itinerary."
            )

        try:
            enriched_destinations = await asyncio.gather(
                *[
                    self._enrich_destination(dest, profile.travel_dates)
                    for dest in destinations
                ]
            )
        except (AzureError, RuntimeError, TimeoutError, TypeError) as exc:
            logger.error(
                "Destination enrichment failed unexpectedly.",
                exc_info=True,
            )
            raise ItineraryGenerationError(
                "The itinerary could not be fully generated."
            ) from exc

        return ItineraryResponse(
            destinations=enriched_destinations,
            generated_at=datetime.now(timezone.utc),
        )

    async def _enrich_destination(
        self,
        destination: Destination,
        travel_dates: TravelDates,
    ) -> Destination:
        """Enrich a destination with POI, event, weather, and advisory.

        Uses concurrent execution to fan-out to specialist agents,
        then merges results back into the destination.

        Args:
            destination: Base destination from General Agent.
            travel_dates: Customer travel date range.

        Returns:
            Enriched destination with POI, events, weather, and
            travel advisory data.
        """
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
        advisory_task = self._safe_call(
            get_travel_advisory,
            destination.name,
            destination.country,
            travel_dates,
            self.settings,
            default=None,
        )

        (
            poi_result,
            event_result,
            weather_result,
            advisory_result,
        ) = await asyncio.gather(
            poi_task,
            event_task,
            weather_task,
            advisory_task,
        )

        if (
            poi_result.failed
            and event_result.failed
            and weather_result.failed
            and advisory_result.failed
        ):
            logger.error(
                "All specialist agents failed for %s, %s.",
                destination.name,
                destination.country,
            )
            raise ItineraryGenerationError(
                "All specialist agents failed while enriching "
                "destination data."
            )

        destination.points_of_interest = poi_result.value
        destination.events = event_result.value
        destination.weather = weather_result.value
        destination.travel_advisory = advisory_result.value

        # Validate enrichment completeness
        missing_enrichments = []
        if not poi_result.value or len(poi_result.value) == 0:
            missing_enrichments.append("points_of_interest")
        if not event_result.value or len(event_result.value) == 0:
            missing_enrichments.append("events")
        if weather_result.value is None:
            missing_enrichments.append("weather")
        if advisory_result.value is None:
            missing_enrichments.append("travel_advisory")

        if missing_enrichments:
            logger.warning(
                "Destination %s, %s is missing enrichment data for: %s",
                destination.name,
                destination.country,
                ", ".join(missing_enrichments),
            )

        return destination

    async def _safe_call(
        self,
        agent_func: Callable[..., Awaitable[T]],
        *args: object,
        default: T,
        **kwargs: object,
    ) -> AgentCallResult[T]:
        """Wrap a specialist agent call with graceful fallback.

        Args:
            agent_func: The specialist agent function to call.
            *args: Positional arguments for the agent function.
            default: Default value to return on failure.
            **kwargs: Keyword arguments for the agent function.

        Returns:
            AgentCallResult[T]: Result value plus failure metadata.
        """
        try:
            result = await agent_func(*args, **kwargs)
            return AgentCallResult(value=result, failed=False)
        except (ApplicationError, AzureError):
            logger.warning(
                "Agent %s failed and will use default fallback.",
                agent_func.__name__,
                exc_info=True,
            )
            return AgentCallResult(value=default, failed=True)
        except (RuntimeError, TimeoutError, TypeError, ValueError):
            logger.warning(
                "Agent %s failed unexpectedly and will use default "
                "fallback.",
                agent_func.__name__,
                exc_info=True,
            )
            return AgentCallResult(value=default, failed=True)
        except Exception:
            logger.warning(
                "Agent %s raised an unhandled exception and will use "
                "default fallback.",
                agent_func.__name__,
                exc_info=True,
            )
            return AgentCallResult(value=default, failed=True)
