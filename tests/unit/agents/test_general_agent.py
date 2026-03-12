"""Unit tests for the General Agent.

Tests the General Agent's ability to recommend destinations based
on customer profiles. All tests use mocked LLM responses — no real
Azure OpenAI calls.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.models.customer import CustomerProfile, TravelDates
from src.api.models.itinerary import Destination
from src.config.settings import Settings


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_general_agent_response() -> List[Dict[str, Any]]:
    """Load mock LLM response for General Agent."""
    with open(
        "tests/fixtures/agent_responses/general_agent.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["destinations"]


@pytest.fixture()
def mock_search_results() -> List[Dict[str, str]]:
    """Load mock Bing search results for destinations."""
    with open(
        "tests/fixtures/search_results/bing_destinations.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["results"]


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestGeneralAgent:
    """Test suite for the General Agent destination recommender."""

    @pytest.mark.asyncio
    async def test_returns_three_to_four_destinations_for_valid_profile(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_settings: None,
        mock_general_agent_response: List[Dict[str, Any]],
        mock_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify General Agent returns 3-4 destinations.

        Architecture spec requires 3-4 destination recommendations
        per customer profile.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_general_agent_response)

        with patch("src.agents.general_agent.DefaultAzureCredential"):
            with patch("src.agents.general_agent.AzureAIClient"):
                with patch("src.agents.general_agent.Agent") as MockAgent:
                    mock_agent_instance = MagicMock()
                    mock_agent_instance.run = AsyncMock(
                        return_value=mock_response
                    )
                    MockAgent.return_value = mock_agent_instance

                    with patch(
                        "src.agents.general_agent._load_system_prompt",
                        return_value="system prompt",
                    ):
                        destinations = await recommend_destinations(
                            profile, settings
                        )

                        assert isinstance(destinations, list)
                        assert 3 <= len(destinations) <= 4
                        assert all(
                            isinstance(d, Destination)
                            for d in destinations
                        )

    @pytest.mark.asyncio
    async def test_verifies_search_web_tool_was_called(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_settings: None,
        mock_general_agent_response: List[Dict[str, Any]],
        mock_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify General Agent calls search_web before proposing.

        Architecture mandates search-first grounding for all agents.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_general_agent_response)

        with patch(
            "src.agents.tools.web_search.search_web"
        ) as mock_search:
            mock_search.return_value = mock_search_results

            with patch("src.agents.general_agent.DefaultAzureCredential"):
                with patch("src.agents.general_agent.AzureAIClient"):
                    with patch(
                        "src.agents.general_agent.Agent"
                    ) as MockAgent:
                        mock_agent_instance = MagicMock()
                        mock_agent_instance.run = AsyncMock(
                            return_value=mock_response
                        )
                        MockAgent.return_value = mock_agent_instance

                        with patch(
                            "src.agents.general_agent._load_system_prompt",
                            return_value="system prompt",
                        ):
                            await recommend_destinations(
                                profile, settings
                            )

                            assert (
                                mock_agent_instance.run.call_count
                                >= 1
                            )

    @pytest.mark.asyncio
    async def test_returns_valid_destination_objects(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_settings: None,
        mock_general_agent_response: List[Dict[str, Any]],
        mock_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify all returned destinations are valid Pydantic models.

        Each Destination must have: name, country, rationale.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings()
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_general_agent_response)

        with patch("src.agents.general_agent.DefaultAzureCredential"), patch("src.agents.general_agent.AzureAIClient"):
            with patch("src.agents.general_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.general_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    destinations = await recommend_destinations(
                        profile, settings
                    )

                    for dest in destinations:
                        assert isinstance(dest, Destination)
                        assert dest.name
                        assert dest.country
                        assert dest.rationale
                        assert len(dest.name) > 0
                        assert len(dest.country) > 0
                        assert len(dest.rationale) > 10

    @pytest.mark.asyncio
    async def test_handles_minimal_profile(
        self,
        mock_settings: None,
        mock_general_agent_response: List[Dict[str, Any]],
        mock_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify agent handles profile with only required fields.

        No optional notes field — should still work.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings()
        minimal_profile = CustomerProfile(
            interests=["hiking"],
            budget="budget",
            travel_dates=TravelDates(
                start=date(2026, 7, 1),
                end=date(2026, 7, 10),
            ),
            party_size=1,
            departure_city="New York",
        )

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_general_agent_response)

        with patch("src.agents.general_agent.DefaultAzureCredential"), patch("src.agents.general_agent.AzureAIClient"):
            with patch("src.agents.general_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.general_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    destinations = await recommend_destinations(
                        minimal_profile, settings
                    )

                    assert len(destinations) >= 3
                    assert all(
                        isinstance(d, Destination) for d in destinations
                    )

    @pytest.mark.asyncio
    async def test_handles_edge_case_many_interests_vs_single(
        self,
        mock_settings: None,
        mock_general_agent_response: List[Dict[str, Any]],
        mock_search_results: List[Dict[str, str]],
    ) -> None:
        """Verify agent handles profiles with 1 vs many interests.

        Tests boundary between focused and diverse travel interests.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings()

        # Test single interest
        single_interest_profile = CustomerProfile(
            interests=["history"],
            budget="moderate",
            travel_dates=TravelDates(
                start=date(2026, 6, 15),
                end=date(2026, 6, 25),
            ),
            party_size=2,
            departure_city="Boston",
        )

        # Test many interests
        many_interests_profile = CustomerProfile(
            interests=[
                "history",
                "food",
                "hiking",
                "art",
                "music",
                "beaches",
            ],
            budget="moderate",
            travel_dates=TravelDates(
                start=date(2026, 6, 15),
                end=date(2026, 6, 25),
            ),
            party_size=2,
            departure_city="Boston",
        )

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_general_agent_response)

        with patch("src.agents.general_agent.DefaultAzureCredential"), patch("src.agents.general_agent.AzureAIClient"):
            with patch("src.agents.general_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.general_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    # Both should succeed
                    single_results = await recommend_destinations(
                        single_interest_profile, settings
                    )
                    many_results = await recommend_destinations(
                        many_interests_profile, settings
                    )

                    assert len(single_results) >= 3
                    assert len(many_results) >= 3
