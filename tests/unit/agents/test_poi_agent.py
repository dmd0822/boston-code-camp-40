"""Unit tests for the POI Agent.

Tests the POI Agent's ability to recommend points of interest for
destinations. All tests use mocked LLM responses — no real Azure
OpenAI calls.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.models.customer import TravelDates
from src.api.models.itinerary import Destination, PointOfInterest
from src.config.settings import Settings


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_poi_agent_response() -> List[Dict[str, Any]]:
    """Load mock LLM response for POI Agent."""
    with open(
        "tests/fixtures/agent_responses/poi_agent.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["points_of_interest"]


@pytest.fixture()
def mock_poi_search_results() -> List[Dict[str, str]]:
    """Load mock Bing search results for POIs."""
    with open(
        "tests/fixtures/search_results/bing_poi.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["results"]


@pytest.fixture()
def sample_destination_for_poi() -> Destination:
    """Return a simple Destination for POI enrichment."""
    return Destination(
        name="Lisbon",
        country="Portugal",
        rationale="Rich history and great food scene.",
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestPOIAgent:
    """Test suite for the POI Agent."""

    @pytest.mark.asyncio
    async def test_returns_pois_with_source_urls_populated(
        self,
        sample_destination_for_poi: Destination,
        mock_settings: None,
        mock_poi_agent_response: List[Dict[str, Any]],
        mock_poi_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify POI Agent returns POIs with source URLs.

        Grounding requires all POIs to reference their web sources.
        """
        pytest.importorskip("src.agents.poi_agent")
        from src.agents.poi_agent import find_points_of_interest

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_poi_agent_response)

        with patch("src.agents.poi_agent.AzureAIClient"):
            with patch("src.agents.poi_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.poi_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    pois = await find_points_of_interest(
                        sample_destination_for_poi.name,
                        sample_destination_for_poi.country,
                        travel_dates,
                        settings,
                    )

                    assert len(pois) > 0
                    # Check that at least some POIs have source URLs
                    pois_with_urls = [
                        p for p in pois if p.source_url is not None
                    ]
                    assert len(pois_with_urls) > 0

    @pytest.mark.asyncio
    async def test_returns_valid_poi_objects(
        self,
        sample_destination_for_poi: Destination,
        mock_settings: None,
        mock_poi_agent_response: List[Dict[str, Any]],
        mock_poi_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify all POIs are valid PointOfInterest Pydantic models.

        Each POI must have: name, description, category,
        visit_duration_hours.
        """
        pytest.importorskip("src.agents.poi_agent")
        from src.agents.poi_agent import find_points_of_interest

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_poi_agent_response)

        with patch("src.agents.poi_agent.AzureAIClient"):
            with patch("src.agents.poi_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.poi_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    pois = await find_points_of_interest(
                        sample_destination_for_poi.name,
                        sample_destination_for_poi.country,
                        travel_dates,
                        settings,
                    )

                    assert len(pois) > 0
                    for poi in pois:
                        assert isinstance(poi, PointOfInterest)
                        assert poi.name
                        assert poi.description
                        assert poi.category
                        assert poi.visit_duration_hours > 0

    @pytest.mark.asyncio
    async def test_handles_unknown_destination_gracefully(
        self,
        mock_settings: None,
        mock_poi_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify POI Agent returns empty list for obscure destinations.

        Should not crash or fabricate POIs for unknown places.
        """
        pytest.importorskip("src.agents.poi_agent")
        from src.agents.poi_agent import find_points_of_interest

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps([])

        with patch("src.agents.poi_agent.AzureAIClient"):
            with patch("src.agents.poi_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.poi_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    pois = await find_points_of_interest(
                        "Nonexistent Town XYZ",
                        "Nowhere",
                        travel_dates,
                        settings,
                    )

                    # Should return empty list, not crash
                    assert isinstance(pois, list)
                    assert len(pois) == 0

    @pytest.mark.asyncio
    async def test_each_poi_has_required_fields(
        self,
        sample_destination_for_poi: Destination,
        mock_settings: None,
        mock_poi_agent_response: List[Dict[str, Any]],
        mock_poi_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify each POI has all required fields populated.

        Required: name, description, category, visit_duration_hours.
        Optional: source_url (should be present when grounded).
        """
        pytest.importorskip("src.agents.poi_agent")
        from src.agents.poi_agent import find_points_of_interest

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_poi_agent_response)

        with patch("src.agents.poi_agent.AzureAIClient"):
            with patch("src.agents.poi_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.poi_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    pois = await find_points_of_interest(
                        sample_destination_for_poi.name,
                        sample_destination_for_poi.country,
                        travel_dates,
                        settings,
                    )

                    for poi in pois:
                        # Required fields
                        assert poi.name
                        assert len(poi.name) > 0
                        assert poi.description
                        assert len(poi.description) > 5
                        assert poi.category
                        assert poi.visit_duration_hours > 0
                        # visit_duration should be reasonable (0.5-8 hrs)
                        assert 0.5 <= poi.visit_duration_hours <= 8.0
