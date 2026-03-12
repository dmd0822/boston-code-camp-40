"""Stub travel orchestrator — returns mock data in Phase 1.

In Phase 2 this will wire the General Agent (sequential) to
POI / Event / Weather agents (concurrent fan-out / fan-in).
"""

from datetime import date, datetime, timezone
from typing import List

from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import (
    Destination,
    Event,
    EventDates,
    ItineraryResponse,
    PointOfInterest,
    WeatherForecast,
)


class TravelOrchestrator:
    """Orchestrates the agent pipeline for itinerary generation.

    Phase 1 (stub): returns realistic mock data.
    Phase 2: General Agent → fan-out POI/Event/Weather.
    """

    async def generate_itinerary(
        self,
        profile: CustomerProfile,
    ) -> ItineraryResponse:
        """Build an itinerary for the given customer profile.

        Parameters:
            profile: Validated customer preferences.

        Returns:
            ItineraryResponse with destinations and metadata.
        """
        destinations = self._build_mock_destinations(profile)
        return ItineraryResponse(
            destinations=destinations,
            generated_at=datetime.now(timezone.utc),
        )

    # ----------------------------------------------------------
    # Private helpers (mock data for Phase 1)
    # ----------------------------------------------------------

    def _build_mock_destinations(
        self,
        profile: CustomerProfile,
    ) -> List[Destination]:
        """Return hard-coded Lisbon example from architecture doc.

        Parameters:
            profile: Customer profile (unused in stub).

        Returns:
            List of mock Destination objects.
        """
        return [
            Destination(
                name="Lisbon",
                country="Portugal",
                rationale=(
                    "Rich history, world-class food scene, "
                    "mild June weather"
                ),
                points_of_interest=[
                    PointOfInterest(
                        name="Belém Tower",
                        description=(
                            "UNESCO World Heritage Site and iconic "
                            "symbol of Portugal's Age of Discovery"
                        ),
                        category="history",
                        visit_duration_hours=1.5,
                        source_url=(
                            "https://whc.unesco.org/en/list/263"
                        ),
                    ),
                    PointOfInterest(
                        name="Time Out Market",
                        description=(
                            "Gourmet food hall in Mercado da "
                            "Ribeira with top Lisbon chefs"
                        ),
                        category="food",
                        visit_duration_hours=2.0,
                        source_url=(
                            "https://www.timeoutmarket.com/lisboa"
                        ),
                    ),
                ],
                events=[
                    Event(
                        name="Festa de Santo António",
                        dates=EventDates(
                            start=date(2026, 6, 12),
                            end=date(2026, 6, 13),
                        ),
                        description=(
                            "Lisbon's biggest street festival "
                            "with sardine grills, music, and "
                            "parades through Alfama"
                        ),
                        venue="Alfama district",
                        source_url=(
                            "https://www.visitlisboa.com/"
                            "en/events/santo-antonio"
                        ),
                    ),
                ],
                weather=WeatherForecast(
                    avg_high_celsius=27.0,
                    avg_low_celsius=17.0,
                    precipitation_chance="low",
                    clothing_suggestion=(
                        "Light layers, comfortable walking "
                        "shoes, sunscreen"
                    ),
                    source_url=(
                        "https://weatherspark.com/y/32022/"
                        "Average-Weather-in-Lisbon-Portugal"
                    ),
                ),
            ),
            Destination(
                name="Porto",
                country="Portugal",
                rationale=(
                    "Stunning riverside architecture, port "
                    "wine cellars, and vibrant food culture"
                ),
                points_of_interest=[
                    PointOfInterest(
                        name="Livraria Lello",
                        description=(
                            "Historic bookstore with ornate "
                            "neo-Gothic interior and famous "
                            "crimson staircase"
                        ),
                        category="culture",
                        visit_duration_hours=1.0,
                        source_url=(
                            "https://www.livrarialello.pt"
                        ),
                    ),
                ],
                events=[],
                weather=WeatherForecast(
                    avg_high_celsius=24.0,
                    avg_low_celsius=15.0,
                    precipitation_chance="moderate",
                    clothing_suggestion=(
                        "Light jacket for evenings, "
                        "comfortable walking shoes"
                    ),
                    source_url=(
                        "https://weatherspark.com/y/32045/"
                        "Average-Weather-in-Porto-Portugal"
                    ),
                ),
            ),
        ]
