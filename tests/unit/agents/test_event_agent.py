"""Unit tests for the Event Agent.

Tests the Event Agent's ability to find festivals and events during
the travel window. All tests use mocked LLM responses — no real
Azure OpenAI calls.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.models.customer import TravelDates
from src.api.models.itinerary import Destination, Event
from src.config.settings import Settings


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_event_agent_response() -> List[Dict[str, Any]]:
    """Load mock LLM response for Event Agent."""
    with open(
        "tests/fixtures/agent_responses/event_agent.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["events"]


@pytest.fixture()
def mock_event_search_results() -> List[Dict[str, str]]:
    """Load mock Bing search results for events."""
    with open(
        "tests/fixtures/search_results/bing_events.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["results"]


@pytest.fixture()
def sample_destination_for_events() -> Destination:
    """Return a simple Destination for event enrichment."""
    return Destination(
        name="Lisbon",
        country="Portugal",
        rationale="Vibrant culture and summer festivals.",
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestEventAgent:
    """Test suite for the Event Agent."""

    @pytest.mark.asyncio
    async def test_returns_events_within_travel_window_dates(
        self,
        sample_destination_for_events: Destination,
        mock_settings: None,
        mock_event_agent_response: List[Dict[str, Any]],
        mock_event_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify Event Agent only returns events within travel dates.

        Events must overlap with the customer's travel window.
        """
        pytest.importorskip("src.agents.event_agent")
        from src.agents.event_agent import find_events

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_event_agent_response)

        with patch("src.agents.event_agent.DefaultAzureCredential"), patch("src.agents.event_agent.AzureAIClient"):
            with patch("src.agents.event_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.event_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    events = await find_events(
                        sample_destination_for_events.name,
                        sample_destination_for_events.country,
                        travel_dates,
                        settings,
                    )

                    # Verify events overlap with travel window
                    for event in events:
                        # Event must start before or during travel window end
                        assert event.dates.start <= travel_dates.end
                        # Event must end after or during travel window start
                        assert event.dates.end >= travel_dates.start

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_events_match_dates(
        self,
        sample_destination_for_events: Destination,
        mock_settings: None,
        mock_event_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify Event Agent returns empty list when no events found.

        Should never fabricate events — empty list is correct.
        """
        pytest.importorskip("src.agents.event_agent")
        from src.agents.event_agent import find_events

        settings = Settings()
        # Travel dates far in the future with no known events
        travel_dates = TravelDates(
            start=date(2027, 12, 1),
            end=date(2027, 12, 10),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps([])

        with patch("src.agents.event_agent.DefaultAzureCredential"), patch("src.agents.event_agent.AzureAIClient"):
            with patch("src.agents.event_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.event_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    events = await find_events(
                        sample_destination_for_events.name,
                        sample_destination_for_events.country,
                        travel_dates,
                        settings,
                    )

                    assert isinstance(events, list)
                    assert len(events) == 0

    @pytest.mark.asyncio
    async def test_events_have_valid_dates_within_travel_window(
        self,
        sample_destination_for_events: Destination,
        mock_settings: None,
        mock_event_agent_response: List[Dict[str, Any]],
        mock_event_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify all event dates are valid and within window.

        Event start <= end, and overlaps with travel dates.
        """
        pytest.importorskip("src.agents.event_agent")
        from src.agents.event_agent import find_events

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_event_agent_response)

        with patch("src.agents.event_agent.DefaultAzureCredential"), patch("src.agents.event_agent.AzureAIClient"):
            with patch("src.agents.event_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.event_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    events = await find_events(
                        sample_destination_for_events.name,
                        sample_destination_for_events.country,
                        travel_dates,
                        settings,
                    )

                    for event in events:
                        # Event dates must be valid
                        assert event.dates.start <= event.dates.end
                        # Event must overlap with travel window
                        assert event.dates.start <= travel_dates.end
                        assert event.dates.end >= travel_dates.start

    @pytest.mark.asyncio
    async def test_valid_event_objects_with_all_required_fields(
        self,
        sample_destination_for_events: Destination,
        mock_settings: None,
        mock_event_agent_response: List[Dict[str, Any]],
        mock_event_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify each Event has all required fields populated.

        Required: name, dates, description, venue.
        Optional: source_url (should be present when grounded).
        """
        pytest.importorskip("src.agents.event_agent")
        from src.agents.event_agent import find_events

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_event_agent_response)

        with patch("src.agents.event_agent.DefaultAzureCredential"), patch("src.agents.event_agent.AzureAIClient"):
            with patch("src.agents.event_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.event_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    events = await find_events(
                        sample_destination_for_events.name,
                        sample_destination_for_events.country,
                        travel_dates,
                        settings,
                    )

                    assert len(events) > 0
                    for event in events:
                        assert isinstance(event, Event)
                        assert event.name
                        assert len(event.name) > 0
                        assert event.dates
                        assert event.description
                        assert len(event.description) > 10
                        assert event.venue
                        assert len(event.venue) > 0

    @pytest.mark.asyncio
    async def test_handles_destination_with_no_events_gracefully(
        self,
        mock_settings: None,
        mock_event_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify Event Agent handles destinations with no events.

        Small towns or remote areas may have no major festivals —
        should return empty list, not crash.
        """
        pytest.importorskip("src.agents.event_agent")
        from src.agents.event_agent import find_events

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 11, 1),
            end=date(2026, 11, 10),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps([])

        with patch("src.agents.event_agent.DefaultAzureCredential"), patch("src.agents.event_agent.AzureAIClient"):
            with patch("src.agents.event_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.event_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    events = await find_events(
                        "Remote Village",
                        "Iceland",
                        travel_dates,
                        settings,
                    )

                    # Should return empty list
                    assert isinstance(events, list)
                    assert len(events) == 0
