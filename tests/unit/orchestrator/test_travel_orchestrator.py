"""Unit tests for the TravelOrchestrator.

Tests the orchestrator's ability to coordinate the agent pipeline:
1. Sequential General Agent invocation
2. Concurrent POI/Event/Weather agent fan-out
3. Graceful handling of partial failures

All agent functions are mocked — no real Azure OpenAI or Bing
Search API calls.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, patch

import pytest

from src.api.models.customer import CustomerProfile, TravelDates
from src.api.models.itinerary import (
    Destination,
    Event,
    EventDates,
    ItineraryResponse,
    PointOfInterest,
    WeatherForecast,
)
from src.config.settings import Settings
from src.exceptions import (
    ExternalServiceError,
    ExternalServiceTimeoutError,
    ItineraryGenerationError,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def orchestrator_settings() -> Settings:
    """Return a Settings instance for orchestrator tests."""
    return Settings(
        AZURE_AI_PROJECT_ENDPOINT="https://test.services.ai.azure.com/api/projects/test",
        AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o",
    )


@pytest.fixture()
def mock_general_destinations() -> List[Destination]:
    """Return mock destinations from General Agent.

    These destinations have name, country, and rationale only —
    no enrichment yet (empty POI/events/weather).
    """
    return [
        Destination(
            name="Lisbon",
            country="Portugal",
            rationale=(
                "Rich history, world-class food scene, "
                "mild June weather"
            ),
            points_of_interest=[],
            events=[],
            weather=None,
        ),
        Destination(
            name="Porto",
            country="Portugal",
            rationale=(
                "Stunning riverside architecture, port wine "
                "cellars, vibrant food culture"
            ),
            points_of_interest=[],
            events=[],
            weather=None,
        ),
        Destination(
            name="Krakow",
            country="Poland",
            rationale=(
                "Medieval architecture, rich history, and "
                "traditional Polish cuisine"
            ),
            points_of_interest=[],
            events=[],
            weather=None,
        ),
    ]


@pytest.fixture()
def mock_pois() -> List[PointOfInterest]:
    """Return mock POI list for a destination."""
    return [
        PointOfInterest(
            name="Belém Tower",
            description=(
                "UNESCO World Heritage Site and iconic "
                "Lisbon landmark."
            ),
            category="history",
            visit_duration_hours=1.5,
            source_url="https://example.com/belem-tower",
        ),
        PointOfInterest(
            name="Time Out Market",
            description=(
                "Gourmet food hall in Mercado da Ribeira with "
                "top Lisbon chefs."
            ),
            category="food",
            visit_duration_hours=2.0,
            source_url="https://example.com/timeout-market",
        ),
    ]


@pytest.fixture()
def mock_events() -> List[Event]:
    """Return mock event list for a destination."""
    return [
        Event(
            name="Festa de Santo António",
            dates=EventDates(
                start=date(2026, 6, 12),
                end=date(2026, 6, 13),
            ),
            description=(
                "Lisbon's biggest street festival with "
                "parades and sardine grills."
            ),
            venue="Alfama district",
            source_url="https://example.com/santo-antonio",
        ),
    ]


@pytest.fixture()
def mock_weather() -> WeatherForecast:
    """Return mock weather forecast for a destination."""
    return WeatherForecast(
        avg_high_celsius=27.0,
        avg_low_celsius=17.0,
        precipitation_chance="low",
        clothing_suggestion=(
            "Light layers, comfortable walking shoes"
        ),
        source_url="https://example.com/lisbon-weather",
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestTravelOrchestrator:
    """Test suite for the TravelOrchestrator."""

    @pytest.mark.asyncio
    async def test_sequential_then_concurrent_flow(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_pois: List[PointOfInterest],
        mock_events: List[Event],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify General Agent called first, then specialists.

        Architecture requires sequential General Agent, then
        concurrent POI/Event/Weather per destination.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        # Mock all agent functions
        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator."
                    "find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather_fn:
                        # Configure mocks
                        mock_general.return_value = (
                            mock_general_destinations
                        )
                        mock_poi.return_value = mock_pois
                        mock_event.return_value = mock_events
                        mock_weather_fn.return_value = mock_weather

                        # Act
                        orchestrator = TravelOrchestrator(
                            orchestrator_settings
                        )
                        result = await orchestrator.generate_itinerary(
                            profile
                        )

                        # Assert: General Agent called once
                        mock_general.assert_called_once()
                        # Assert: Specialists called once per
                        # destination
                        assert (
                            mock_poi.call_count
                            == len(mock_general_destinations)
                        )
                        assert (
                            mock_event.call_count
                            == len(mock_general_destinations)
                        )
                        assert (
                            mock_weather_fn.call_count
                            == len(mock_general_destinations)
                        )
                        # Assert: Result is valid
                        assert isinstance(result, ItineraryResponse)
                        assert len(result.destinations) == 3

    @pytest.mark.asyncio
    async def test_fan_out_executes_all_three_specialist_agents(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_pois: List[PointOfInterest],
        mock_events: List[Event],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify all 3 specialist agents run per destination.

        POI, Event, and Weather agents must all execute for each
        destination returned by the General Agent.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator."
                    "find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather_fn:
                        mock_general.return_value = (
                            mock_general_destinations
                        )
                        mock_poi.return_value = mock_pois
                        mock_event.return_value = mock_events
                        mock_weather_fn.return_value = mock_weather

                        orchestrator = TravelOrchestrator(
                            orchestrator_settings
                        )
                        await orchestrator.generate_itinerary(
                            profile
                        )

                        # Assert: All 3 agents called for each
                        # destination
                        num_destinations = len(
                            mock_general_destinations
                        )
                        assert mock_poi.call_count == num_destinations
                        assert (
                            mock_event.call_count == num_destinations
                        )
                        assert (
                            mock_weather_fn.call_count
                            == num_destinations
                        )

    @pytest.mark.asyncio
    async def test_partial_failure_returns_partial_itinerary(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_events: List[Event],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify partial failure doesn't crash the orchestrator.

        If POI agent fails, events and weather should still be
        returned (not a 500 error).
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator."
                    "find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather_fn:
                        mock_general.return_value = (
                            mock_general_destinations
                        )
                        # POI agent fails
                        mock_poi.side_effect = ExternalServiceError(
                            "POI agent error"
                        )
                        mock_event.return_value = mock_events
                        mock_weather_fn.return_value = mock_weather

                        orchestrator = TravelOrchestrator(
                            orchestrator_settings
                        )
                        result = await orchestrator.generate_itinerary(
                            profile
                        )

                        # Assert: Partial result returned, not crash
                        assert isinstance(result, ItineraryResponse)
                        assert len(result.destinations) > 0
                        # POIs should be empty (failed), but events
                        # and weather present
                        for dest in result.destinations:
                            assert dest.points_of_interest == []
                            # If orchestrator handles partial failure
                            # gracefully, events/weather may still be
                            # present

    @pytest.mark.asyncio
    async def test_general_agent_failure_raises_external_service_error(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
    ) -> None:
        """Verify General Agent failures do not masquerade as success."""
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            mock_general.side_effect = ExternalServiceError(
                "General Agent error"
            )

            orchestrator = TravelOrchestrator(
                orchestrator_settings
            )

            with pytest.raises(ExternalServiceError):
                await orchestrator.generate_itinerary(profile)

    @pytest.mark.asyncio
    async def test_returns_valid_itinerary_response(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_pois: List[PointOfInterest],
        mock_events: List[Event],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify output is a valid ItineraryResponse.

        Output must have destinations list and generated_at
        timestamp.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator."
                    "find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather_fn:
                        mock_general.return_value = (
                            mock_general_destinations
                        )
                        mock_poi.return_value = mock_pois
                        mock_event.return_value = mock_events
                        mock_weather_fn.return_value = mock_weather

                        orchestrator = TravelOrchestrator(
                            orchestrator_settings
                        )
                        result = await orchestrator.generate_itinerary(
                            profile
                        )

                        # Assert: Valid ItineraryResponse structure
                        assert isinstance(result, ItineraryResponse)
                        assert isinstance(result.destinations, list)
                        assert isinstance(
                            result.generated_at, datetime
                        )
                        assert all(
                            isinstance(d, Destination)
                            for d in result.destinations
                        )

    @pytest.mark.asyncio
    async def test_multiple_destinations_enriched(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_pois: List[PointOfInterest],
        mock_events: List[Event],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify all destinations get enriched.

        If General Agent returns 3 destinations, all 3 should
        be enriched with POI/Event/Weather data.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator."
                    "find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather_fn:
                        mock_general.return_value = (
                            mock_general_destinations
                        )
                        mock_poi.return_value = mock_pois
                        mock_event.return_value = mock_events
                        mock_weather_fn.return_value = mock_weather

                        orchestrator = TravelOrchestrator(
                            orchestrator_settings
                        )
                        result = await orchestrator.generate_itinerary(
                            profile
                        )

                        # Assert: All destinations enriched
                        assert len(result.destinations) == 3
                        for dest in result.destinations:
                            # Each destination should have
                            # enrichment data
                            assert (
                                len(dest.points_of_interest) > 0
                            )
                            assert dest.weather is not None
                            # Events may be empty (no events in
                            # time window)

    @pytest.mark.asyncio
    async def test_weather_agent_failure_still_returns_poi_and_events(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_pois: List[PointOfInterest],
        mock_events: List[Event],
    ) -> None:
        """Verify weather failures degrade gracefully per destination."""
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general, patch(
            "src.orchestrator.travel_orchestrator."
            "find_points_of_interest",
            new_callable=AsyncMock,
        ) as mock_poi, patch(
            "src.orchestrator.travel_orchestrator."
            "find_events",
            new_callable=AsyncMock,
        ) as mock_event, patch(
            "src.orchestrator.travel_orchestrator."
            "get_weather_forecast",
            new_callable=AsyncMock,
        ) as mock_weather_fn:
            mock_general.return_value = mock_general_destinations
            mock_poi.return_value = mock_pois
            mock_event.return_value = mock_events
            mock_weather_fn.side_effect = ExternalServiceError(
                "Weather agent unavailable"
            )

            orchestrator = TravelOrchestrator(orchestrator_settings)
            result = await orchestrator.generate_itinerary(profile)

        assert len(result.destinations) == len(mock_general_destinations)
        for destination in result.destinations:
            assert destination.points_of_interest == mock_pois
            assert destination.events == mock_events
            assert destination.weather is None

    @pytest.mark.asyncio
    async def test_poi_agent_failure_still_returns_weather_and_events(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_events: List[Event],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify POI failures do not drop other specialist data."""
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general, patch(
            "src.orchestrator.travel_orchestrator."
            "find_points_of_interest",
            new_callable=AsyncMock,
        ) as mock_poi, patch(
            "src.orchestrator.travel_orchestrator."
            "find_events",
            new_callable=AsyncMock,
        ) as mock_event, patch(
            "src.orchestrator.travel_orchestrator."
            "get_weather_forecast",
            new_callable=AsyncMock,
        ) as mock_weather_fn:
            mock_general.return_value = mock_general_destinations
            mock_poi.side_effect = ExternalServiceError(
                "POI agent unavailable"
            )
            mock_event.return_value = mock_events
            mock_weather_fn.return_value = mock_weather

            orchestrator = TravelOrchestrator(orchestrator_settings)
            result = await orchestrator.generate_itinerary(profile)

        assert len(result.destinations) == len(mock_general_destinations)
        for destination in result.destinations:
            assert destination.points_of_interest == []
            assert destination.events == mock_events
            assert destination.weather == mock_weather

    @pytest.mark.asyncio
    async def test_all_specialist_agent_failures_raise_generation_error(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
    ) -> None:
        """Verify total specialist failure becomes a hard error."""
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general, patch(
            "src.orchestrator.travel_orchestrator."
            "find_points_of_interest",
            new_callable=AsyncMock,
        ) as mock_poi, patch(
            "src.orchestrator.travel_orchestrator."
            "find_events",
            new_callable=AsyncMock,
        ) as mock_event, patch(
            "src.orchestrator.travel_orchestrator."
            "get_weather_forecast",
            new_callable=AsyncMock,
        ) as mock_weather_fn:
            mock_general.return_value = mock_general_destinations
            mock_poi.side_effect = ExternalServiceError(
                "POI agent failed"
            )
            mock_event.side_effect = ExternalServiceError(
                "Event agent failed"
            )
            mock_weather_fn.side_effect = ExternalServiceError(
                "Weather agent failed"
            )

            orchestrator = TravelOrchestrator(orchestrator_settings)

            with pytest.raises(ItineraryGenerationError):
                await orchestrator.generate_itinerary(profile)

    @pytest.mark.asyncio
    async def test_timeout_during_fan_out_preserves_completed_results(
        self,
        sample_customer_profile: Dict[str, Any],
        orchestrator_settings: Settings,
        mock_general_destinations: List[Destination],
        mock_pois: List[PointOfInterest],
        mock_weather: WeatherForecast,
    ) -> None:
        """Verify specialist timeouts do not cancel successful peers."""
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator."
            "recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general, patch(
            "src.orchestrator.travel_orchestrator."
            "find_points_of_interest",
            new_callable=AsyncMock,
        ) as mock_poi, patch(
            "src.orchestrator.travel_orchestrator."
            "find_events",
            new_callable=AsyncMock,
        ) as mock_event, patch(
            "src.orchestrator.travel_orchestrator."
            "get_weather_forecast",
            new_callable=AsyncMock,
        ) as mock_weather_fn:
            mock_general.return_value = mock_general_destinations
            mock_poi.return_value = mock_pois
            mock_event.side_effect = ExternalServiceTimeoutError(
                "Event agent timed out"
            )
            mock_weather_fn.return_value = mock_weather

            orchestrator = TravelOrchestrator(orchestrator_settings)
            result = await orchestrator.generate_itinerary(profile)

        assert mock_poi.call_count == len(mock_general_destinations)
        assert mock_weather_fn.call_count == len(mock_general_destinations)
        for destination in result.destinations:
            assert destination.points_of_interest == mock_pois
            assert destination.events == []
            assert destination.weather == mock_weather
