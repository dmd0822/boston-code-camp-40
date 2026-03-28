"""Unit tests for orchestrator enrichment validation.

Tests that validate the orchestrator's enrichment guarantees:
- All 4 enrichment types (POI, events, weather, travel_advisory) are
  attempted for each destination
- Graceful degradation when individual enrichments fail
- Logging warnings for missing enrichments
- Minimum 3 destinations requirement at orchestrator level
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, patch

import pytest

from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import (
    Destination,
    Event,
    EventDates,
    PointOfInterest,
    TravelAdvisory,
    WeatherForecast,
)
from src.config.settings import Settings
from src.exceptions import (
    ExternalServiceError,
    ItineraryGenerationError,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def three_destinations() -> List[Destination]:
    """Return exactly 3 destinations from General Agent.

    Meets the minimum requirement for destination count.
    """
    return [
        Destination(
            name="Paris",
            country="France",
            rationale="Perfect blend of history, food, and culture",
        ),
        Destination(
            name="Rome",
            country="Italy",
            rationale="Ancient history and world-class cuisine",
        ),
        Destination(
            name="Barcelona",
            country="Spain",
            rationale="Vibrant architecture and Mediterranean charm",
        ),
    ]


@pytest.fixture()
def complete_enrichments() -> Dict[str, Any]:
    """Return complete enrichment data (all 4 types).

    Includes POI, events, weather, and travel advisory.
    """
    return {
        "pois": [
            PointOfInterest(
                name="Test POI",
                description="A test point of interest",
                category="history",
                visit_duration_hours=2.0,
                source_url="https://example.com/poi",
            )
        ],
        "events": [
            Event(
                name="Test Event",
                dates=EventDates(
                    start=date(2026, 6, 15),
                    end=date(2026, 6, 17),
                ),
                description="A test event",
                venue="Test Venue",
                source_url="https://example.com/event",
            )
        ],
        "weather": WeatherForecast(
            avg_high_celsius=24.0,
            avg_low_celsius=15.0,
            precipitation_chance="low",
            clothing_suggestion="Light layers",
            source_url="https://example.com/weather",
        ),
        "advisory": TravelAdvisory(
            advisory_level=1,
            advisory_summary="Exercise normal precautions",
            specific_warnings=["Be aware of your surroundings"],
            last_updated="2026-05-01",
            source_url="https://travel.state.gov",
        ),
    }


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestOrchestratorEnrichmentValidation:
    """Test suite for orchestrator enrichment validation."""

    @pytest.mark.asyncio
    async def test_all_four_enrichments_attempted(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify all 4 enrichment types are attempted per destination.

        Architecture requirement: Orchestrator must attempt to enrich
        each destination with POI, events, weather, and travel advisory.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.return_value = complete_enrichments[
                                "pois"
                            ]
                            mock_event.return_value = (
                                complete_enrichments["events"]
                            )
                            mock_weather.return_value = (
                                complete_enrichments["weather"]
                            )
                            mock_advisory.return_value = (
                                complete_enrichments["advisory"]
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: All 4 enrichment functions called
                            # for each destination
                            assert (
                                mock_poi.call_count
                                == len(three_destinations)
                            )
                            assert (
                                mock_event.call_count
                                == len(three_destinations)
                            )
                            assert (
                                mock_weather.call_count
                                == len(three_destinations)
                            )
                            assert (
                                mock_advisory.call_count
                                == len(three_destinations)
                            )

                            # Assert: All destinations have all 4
                            # enrichments
                            for dest in result.destinations:
                                assert len(dest.points_of_interest) > 0
                                assert len(dest.events) > 0
                                assert dest.weather is not None
                                assert dest.travel_advisory is not None

    @pytest.mark.asyncio
    async def test_missing_poi_logs_warning_but_continues(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify missing POI logs a warning but allows continuation.

        Graceful degradation: POI enrichment failures should not
        prevent other enrichments from succeeding.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks: POI fails, others succeed
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.side_effect = ExternalServiceError(
                                "POI service failed"
                            )
                            mock_event.return_value = (
                                complete_enrichments["events"]
                            )
                            mock_weather.return_value = (
                                complete_enrichments["weather"]
                            )
                            mock_advisory.return_value = (
                                complete_enrichments["advisory"]
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: Result is still successful
                            assert len(result.destinations) == 3

                            # Assert: POI is empty, others populated
                            for dest in result.destinations:
                                assert (
                                    len(dest.points_of_interest) == 0
                                )
                                assert len(dest.events) > 0
                                assert dest.weather is not None
                                assert dest.travel_advisory is not None

    @pytest.mark.asyncio
    async def test_missing_events_logs_warning_but_continues(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify missing events logs a warning but allows continuation.

        Graceful degradation: Event enrichment failures should not
        prevent other enrichments from succeeding.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks: Events fail, others
                            # succeed
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.return_value = complete_enrichments[
                                "pois"
                            ]
                            mock_event.side_effect = ExternalServiceError(
                                "Event service failed"
                            )
                            mock_weather.return_value = (
                                complete_enrichments["weather"]
                            )
                            mock_advisory.return_value = (
                                complete_enrichments["advisory"]
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: Result is still successful
                            assert len(result.destinations) == 3

                            # Assert: Events are empty, others populated
                            for dest in result.destinations:
                                assert len(dest.points_of_interest) > 0
                                assert len(dest.events) == 0
                                assert dest.weather is not None
                                assert dest.travel_advisory is not None

    @pytest.mark.asyncio
    async def test_missing_weather_logs_warning_but_continues(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify missing weather logs a warning but allows continuation.

        Graceful degradation: Weather enrichment failures should not
        prevent other enrichments from succeeding.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks: Weather fails, others
                            # succeed
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.return_value = complete_enrichments[
                                "pois"
                            ]
                            mock_event.return_value = (
                                complete_enrichments["events"]
                            )
                            mock_weather.side_effect = (
                                ExternalServiceError(
                                    "Weather service failed"
                                )
                            )
                            mock_advisory.return_value = (
                                complete_enrichments["advisory"]
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: Result is still successful
                            assert len(result.destinations) == 3

                            # Assert: Weather is None, others populated
                            for dest in result.destinations:
                                assert len(dest.points_of_interest) > 0
                                assert len(dest.events) > 0
                                assert dest.weather is None
                                assert dest.travel_advisory is not None

    @pytest.mark.asyncio
    async def test_missing_advisory_logs_warning_but_continues(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify missing advisory logs a warning but allows continuation.

        Graceful degradation: Travel advisory failures should not
        prevent other enrichments from succeeding.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks: Advisory fails, others
                            # succeed
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.return_value = complete_enrichments[
                                "pois"
                            ]
                            mock_event.return_value = (
                                complete_enrichments["events"]
                            )
                            mock_weather.return_value = (
                                complete_enrichments["weather"]
                            )
                            mock_advisory.side_effect = (
                                ExternalServiceError(
                                    "Advisory service failed"
                                )
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: Result is still successful
                            assert len(result.destinations) == 3

                            # Assert: Advisory is None, others populated
                            for dest in result.destinations:
                                assert len(dest.points_of_interest) > 0
                                assert len(dest.events) > 0
                                assert dest.weather is not None
                                assert dest.travel_advisory is None

    @pytest.mark.asyncio
    async def test_all_enrichments_fail_raises_error(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
    ) -> None:
        """Verify all enrichments failing raises an error.

        If all 4 enrichment types fail for a destination, the
        orchestrator should raise an ItineraryGenerationError.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks: All enrichments fail
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.side_effect = ExternalServiceError(
                                "POI service failed"
                            )
                            mock_event.side_effect = (
                                ExternalServiceError(
                                    "Event service failed"
                                )
                            )
                            mock_weather.side_effect = (
                                ExternalServiceError(
                                    "Weather service failed"
                                )
                            )
                            mock_advisory.side_effect = (
                                ExternalServiceError(
                                    "Advisory service failed"
                                )
                            )

                            # Act & Assert
                            orchestrator = TravelOrchestrator(settings)
                            with pytest.raises(
                                ItineraryGenerationError
                            ):
                                await orchestrator.generate_itinerary(
                                    profile
                                )

    @pytest.mark.asyncio
    async def test_minimum_three_destinations_gate(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify orchestrator accepts exactly 3 destinations.

        Architecture requirement: Orchestrator should accept
        General Agent results with at least 3 destinations.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks with exactly 3 destinations
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.return_value = complete_enrichments[
                                "pois"
                            ]
                            mock_event.return_value = (
                                complete_enrichments["events"]
                            )
                            mock_weather.return_value = (
                                complete_enrichments["weather"]
                            )
                            mock_advisory.return_value = (
                                complete_enrichments["advisory"]
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: Exactly 3 destinations in result
                            assert len(result.destinations) == 3

    @pytest.mark.asyncio
    async def test_partial_enrichment_still_returns_results(
        self,
        sample_customer_profile: Dict[str, Any],
        three_destinations: List[Destination],
        complete_enrichments: Dict[str, Any],
    ) -> None:
        """Verify partial enrichment failures don't block results.

        Graceful degradation: Even if 2 out of 4 enrichments fail,
        the orchestrator should return results with the successful
        enrichments.
        """
        pytest.importorskip("src.orchestrator.travel_orchestrator")
        from src.orchestrator.travel_orchestrator import (
            TravelOrchestrator,
        )

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        with patch(
            "src.orchestrator.travel_orchestrator.recommend_destinations",
            new_callable=AsyncMock,
        ) as mock_general:
            with patch(
                "src.orchestrator.travel_orchestrator."
                "find_points_of_interest",
                new_callable=AsyncMock,
            ) as mock_poi:
                with patch(
                    "src.orchestrator.travel_orchestrator.find_events",
                    new_callable=AsyncMock,
                ) as mock_event:
                    with patch(
                        "src.orchestrator.travel_orchestrator."
                        "get_weather_forecast",
                        new_callable=AsyncMock,
                    ) as mock_weather:
                        with patch(
                            "src.orchestrator.travel_orchestrator."
                            "get_travel_advisory",
                            new_callable=AsyncMock,
                        ) as mock_advisory:
                            # Configure mocks: POI and Events succeed,
                            # Weather and Advisory fail
                            mock_general.return_value = (
                                three_destinations
                            )
                            mock_poi.return_value = complete_enrichments[
                                "pois"
                            ]
                            mock_event.return_value = (
                                complete_enrichments["events"]
                            )
                            mock_weather.side_effect = (
                                ExternalServiceError(
                                    "Weather service failed"
                                )
                            )
                            mock_advisory.side_effect = (
                                ExternalServiceError(
                                    "Advisory service failed"
                                )
                            )

                            # Act
                            orchestrator = TravelOrchestrator(settings)
                            result = (
                                await orchestrator.generate_itinerary(
                                    profile
                                )
                            )

                            # Assert: Result is still successful
                            assert len(result.destinations) == 3

                            # Assert: Partial enrichment present
                            for dest in result.destinations:
                                assert len(dest.points_of_interest) > 0
                                assert len(dest.events) > 0
                                assert dest.weather is None
                                assert dest.travel_advisory is None
