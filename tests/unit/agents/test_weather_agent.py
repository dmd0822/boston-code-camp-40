"""Unit tests for the Weather Agent.

Tests the Weather Agent's ability to provide historical weather
forecasts for destinations. All tests use mocked LLM responses —
no real Azure OpenAI calls.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.models.customer import TravelDates
from src.api.models.itinerary import Destination, WeatherForecast
from src.config.settings import Settings


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_weather_agent_response() -> Dict[str, Any]:
    """Load mock LLM response for Weather Agent."""
    with open(
        "tests/fixtures/agent_responses/weather_agent.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["weather"]


@pytest.fixture()
def mock_weather_search_results() -> list:
    """Load mock Bing search results for weather."""
    with open(
        "tests/fixtures/search_results/bing_weather.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
        return data["results"]


@pytest.fixture()
def sample_destination_for_weather() -> Destination:
    """Return a simple Destination for weather enrichment."""
    return Destination(
        name="Lisbon",
        country="Portugal",
        rationale="Warm Mediterranean climate.",
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestWeatherAgent:
    """Test suite for the Weather Agent."""

    @pytest.mark.asyncio
    async def test_returns_plausible_temperature_ranges(
        self,
        sample_destination_for_weather: Destination,
        mock_settings: None,
        mock_weather_agent_response: Dict[str, Any],
        mock_weather_search_results: list,
    ) -> None:
        """Verify Weather Agent returns realistic temperature ranges.

        Temperatures should be within reasonable bounds for Earth
        climates (-60°C to 60°C). Low should be less than high.
        """
        pytest.importorskip("src.agents.weather_agent")
        from src.agents.weather_agent import get_weather_forecast

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_weather_agent_response)

        with patch("src.agents.weather_agent.DefaultAzureCredential"), patch("src.agents.weather_agent.AzureAIClient"):
            with patch("src.agents.weather_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.weather_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    weather = await get_weather_forecast(
                        sample_destination_for_weather.name,
                        sample_destination_for_weather.country,
                        travel_dates,
                        settings,
                    )

                    assert isinstance(weather, WeatherForecast)
                    # Temperatures should be within plausible range
                    assert -60 <= weather.avg_high_celsius <= 60
                    assert -60 <= weather.avg_low_celsius <= 60
                    # Low should be less than high
                    assert (
                        weather.avg_low_celsius < weather.avg_high_celsius
                    )

    @pytest.mark.asyncio
    async def test_includes_clothing_suggestions(
        self,
        sample_destination_for_weather: Destination,
        mock_settings: None,
        mock_weather_agent_response: Dict[str, Any],
        mock_weather_search_results: list,
    ) -> None:
        """Verify Weather Agent provides clothing suggestions.

        Clothing advice helps travelers pack appropriately.
        """
        pytest.importorskip("src.agents.weather_agent")
        from src.agents.weather_agent import get_weather_forecast

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_weather_agent_response)

        with patch("src.agents.weather_agent.DefaultAzureCredential"), patch("src.agents.weather_agent.AzureAIClient"):
            with patch("src.agents.weather_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.weather_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    weather = await get_weather_forecast(
                        sample_destination_for_weather.name,
                        sample_destination_for_weather.country,
                        travel_dates,
                        settings,
                    )

                    assert weather.clothing_suggestion
                    assert len(weather.clothing_suggestion) > 10
                    # Should contain practical clothing terms
                    suggestion_lower = (
                        weather.clothing_suggestion.lower()
                    )
                    clothing_terms = [
                        "layer",
                        "jacket",
                        "shoes",
                        "light",
                        "warm",
                        "sunscreen",
                        "coat",
                        "comfortable",
                    ]
                    assert any(
                        term in suggestion_lower for term in clothing_terms
                    )

    @pytest.mark.asyncio
    async def test_returns_valid_weather_forecast_object(
        self,
        sample_destination_for_weather: Destination,
        mock_settings: None,
        mock_weather_agent_response: Dict[str, Any],
        mock_weather_search_results: list,
    ) -> None:
        """Verify Weather Agent returns valid WeatherForecast model.

        Required fields: avg_high_celsius, avg_low_celsius,
        precipitation_chance, clothing_suggestion.
        """
        pytest.importorskip("src.agents.weather_agent")
        from src.agents.weather_agent import get_weather_forecast

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_weather_agent_response)

        with patch("src.agents.weather_agent.DefaultAzureCredential"), patch("src.agents.weather_agent.AzureAIClient"):
            with patch("src.agents.weather_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.weather_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    weather = await get_weather_forecast(
                        sample_destination_for_weather.name,
                        sample_destination_for_weather.country,
                        travel_dates,
                        settings,
                    )

                    assert isinstance(weather, WeatherForecast)
                    assert isinstance(
                        weather.avg_high_celsius, (int, float)
                    )
                    assert isinstance(
                        weather.avg_low_celsius, (int, float)
                    )
                    assert weather.precipitation_chance
                    assert weather.clothing_suggestion

    @pytest.mark.asyncio
    async def test_handles_unknown_destination_gracefully(
        self,
        mock_settings: None,
        mock_weather_search_results: list,
    ) -> None:
        """Verify Weather Agent handles unknown destinations.

        Should return None or raise appropriate error, not crash.
        """
        pytest.importorskip("src.agents.weather_agent")
        from src.agents.weather_agent import get_weather_forecast

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = "null"

        with patch("src.agents.weather_agent.DefaultAzureCredential"), patch("src.agents.weather_agent.AzureAIClient"):
            with patch("src.agents.weather_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.weather_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    weather = await get_weather_forecast(
                        "Fake City XYZ",
                        "Unknown",
                        travel_dates,
                        settings,
                    )

                    # Should return None for unknown destinations
                    assert weather is None

    @pytest.mark.asyncio
    async def test_precipitation_chance_is_reasonable_value(
        self,
        sample_destination_for_weather: Destination,
        mock_settings: None,
        mock_weather_agent_response: Dict[str, Any],
        mock_weather_search_results: list,
    ) -> None:
        """Verify precipitation_chance is a reasonable value.

        Should be descriptive text like 'low', 'moderate', 'high'
        or percentage, not nonsense values.
        """
        pytest.importorskip("src.agents.weather_agent")
        from src.agents.weather_agent import get_weather_forecast

        settings = Settings()
        travel_dates = TravelDates(
            start=date(2026, 6, 15),
            end=date(2026, 6, 25),
        )

        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_weather_agent_response)

        with patch("src.agents.weather_agent.DefaultAzureCredential"), patch("src.agents.weather_agent.AzureAIClient"):
            with patch("src.agents.weather_agent.Agent") as MockAgent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.run = AsyncMock(
                    return_value=mock_response
                )
                MockAgent.return_value = mock_agent_instance

                with patch(
                    "src.agents.weather_agent._load_system_prompt",
                    return_value="system prompt",
                ):
                    weather = await get_weather_forecast(
                        sample_destination_for_weather.name,
                        sample_destination_for_weather.country,
                        travel_dates,
                        settings,
                    )

                    assert weather.precipitation_chance
                    precip_lower = weather.precipitation_chance.lower()
                    # Should contain reasonable descriptors
                    valid_terms = [
                        "low",
                        "moderate",
                        "high",
                        "rare",
                        "common",
                        "%",
                        "percent",
                        "unlikely",
                        "likely",
                    ]
                    assert any(term in precip_lower for term in valid_terms)
