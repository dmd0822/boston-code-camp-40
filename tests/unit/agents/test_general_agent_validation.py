"""Unit tests for General Agent destination count validation.

Tests the validation logic that ensures General Agent returns
a minimum of 3 destinations. These tests validate the guarantees
that Batty is implementing as part of the minimum trip requirement.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.models.customer import CustomerProfile
from src.config.settings import Settings
from src.exceptions import ExternalServiceError


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_destinations_response_factory() -> callable:
    """Factory to create mock destination responses with N destinations."""

    def _factory(count: int) -> List[Dict[str, Any]]:
        """Create a list of mock destinations.

        Args:
            count: Number of destinations to create.

        Returns:
            List of destination dictionaries.
        """
        destinations = []
        cities = [
            ("Paris", "France"),
            ("Rome", "Italy"),
            ("Barcelona", "Spain"),
            ("Lisbon", "Portugal"),
            ("Amsterdam", "Netherlands"),
        ]
        for i in range(count):
            city, country = cities[i % len(cities)]
            destinations.append(
                {
                    "name": f"{city}{i if i >= len(cities) else ''}",
                    "country": country,
                    "rationale": f"Great destination {i+1}",
                }
            )
        return destinations

    return _factory


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestGeneralAgentMinimumDestinations:
    """Test suite for General Agent minimum destination validation."""

    @pytest.mark.asyncio
    async def test_zero_destinations_raises_error(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_destinations_response_factory: callable,
    ) -> None:
        """Verify zero destinations raises an error.

        Architecture requirement: General Agent must return at least
        3 destinations. Zero destinations is a validation failure.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings(
            AZURE_AI_PROJECT_ENDPOINT="https://test.services.ai.azure.com/api/projects/test",
            AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o",
        )
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(
            mock_destinations_response_factory(0)
        )

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
                        # Zero destinations should raise error
                        with pytest.raises(ExternalServiceError) as exc:
                            await recommend_destinations(
                                profile, settings
                            )

                        assert "at least 3 are required" in str(
                            exc.value
                        )

    @pytest.mark.asyncio
    async def test_one_destination_insufficient(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_destinations_response_factory: callable,
    ) -> None:
        """Verify one destination is insufficient.

        Architecture requirement: General Agent must return at least
        3 destinations. One destination does not meet the minimum.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings(
            AZURE_AI_PROJECT_ENDPOINT="https://test.services.ai.azure.com/api/projects/test",
            AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o",
        )
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(
            mock_destinations_response_factory(1)
        )

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
                        # One destination should raise error
                        with pytest.raises(ExternalServiceError) as exc:
                            await recommend_destinations(
                                profile, settings
                            )

                        assert "at least 3 are required" in str(
                            exc.value
                        )

    @pytest.mark.asyncio
    async def test_two_destinations_insufficient(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_destinations_response_factory: callable,
    ) -> None:
        """Verify two destinations are insufficient.

        Architecture requirement: General Agent must return at least
        3 destinations. Two destinations do not meet the minimum.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings(
            AZURE_AI_PROJECT_ENDPOINT="https://test.services.ai.azure.com/api/projects/test",
            AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o",
        )
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(
            mock_destinations_response_factory(2)
        )

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
                        # Two destinations should raise error
                        with pytest.raises(ExternalServiceError) as exc:
                            await recommend_destinations(
                                profile, settings
                            )

                        assert "at least 3 are required" in str(
                            exc.value
                        )

    @pytest.mark.asyncio
    async def test_three_destinations_meets_minimum(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_destinations_response_factory: callable,
    ) -> None:
        """Verify three destinations meets the minimum requirement.

        Architecture requirement: General Agent must return at least
        3 destinations. Three destinations is the minimum acceptable.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings(
            AZURE_AI_PROJECT_ENDPOINT="https://test.services.ai.azure.com/api/projects/test",
            AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o",
        )
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(
            mock_destinations_response_factory(3)
        )

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

                        assert len(destinations) == 3
                        # Verify all destinations have required fields
                        for dest in destinations:
                            assert dest.name
                            assert dest.country
                            assert dest.rationale

    @pytest.mark.asyncio
    async def test_four_destinations_exceeds_minimum(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_destinations_response_factory: callable,
    ) -> None:
        """Verify four destinations exceeds minimum requirement.

        Architecture spec allows 3-4 destinations. Four destinations
        is acceptable and exceeds the minimum.
        """
        pytest.importorskip("src.agents.general_agent")
        from src.agents.general_agent import recommend_destinations

        settings = Settings(
            AZURE_AI_PROJECT_ENDPOINT="https://test.services.ai.azure.com/api/projects/test",
            AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o",
        )
        profile = CustomerProfile(**sample_customer_profile)

        mock_response = MagicMock()
        mock_response.text = json.dumps(
            mock_destinations_response_factory(4)
        )

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

                        assert len(destinations) == 4
                        # Verify all destinations have required fields
                        for dest in destinations:
                            assert dest.name
                            assert dest.country
                            assert dest.rationale
