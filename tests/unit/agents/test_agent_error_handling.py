"""Shared error-handling contract tests for all backend agents.

These tests define how agent wrappers should behave when upstream
services fail or the LLM returns malformed output. They intentionally
exercise the public agent functions rather than implementation details.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.exceptions import ServiceRequestError

from src.api.models.customer import CustomerProfile, TravelDates
from src.config.settings import Settings
from src.exceptions import ExternalServiceError

AGENT_CASES = (
    (
        "general",
        "src.agents.general_agent",
        "create_general_agent",
        "recommend_destinations",
        [],
    ),
    (
        "poi",
        "src.agents.poi_agent",
        "create_poi_agent",
        "find_points_of_interest",
        [],
    ),
    (
        "event",
        "src.agents.event_agent",
        "create_event_agent",
        "find_events",
        [],
    ),
    (
        "weather",
        "src.agents.weather_agent",
        "create_weather_agent",
        "get_weather_forecast",
        None,
    ),
)


def _build_agent_args(
    agent_kind: str,
    sample_customer_profile: Dict[str, Any],
) -> Tuple[Any, ...]:
    """Build valid public-call arguments for each agent wrapper."""
    settings = Settings()

    if agent_kind == "general":
        profile = CustomerProfile(**sample_customer_profile)
        return (profile, settings)

    travel_dates = TravelDates(
        start=date(2026, 6, 15),
        end=date(2026, 6, 25),
    )
    return ("Lisbon", "Portugal", travel_dates, settings)


class TestAgentErrorHandling:
    """Contract tests for backend agent fallback behavior."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        (
            "agent_kind",
            "module_name",
            "factory_name",
            "function_name",
            "expected_default",
        ),
        AGENT_CASES,
        ids=[case[0] for case in AGENT_CASES],
    )
    async def test_azure_openai_failures_raise_external_service_error(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_settings: None,
        agent_kind: str,
        module_name: str,
        factory_name: str,
        function_name: str,
        expected_default: Any,
    ) -> None:
        """Verify Azure OpenAI errors become typed service failures."""
        module = pytest.importorskip(module_name)
        agent_function = getattr(module, function_name)

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(
            side_effect=ServiceRequestError("Azure OpenAI API error")
        )

        with patch(
            f"{module_name}.{factory_name}",
            return_value=mock_agent,
        ):
            with pytest.raises(ExternalServiceError):
                await agent_function(
                    *_build_agent_args(
                        agent_kind,
                        sample_customer_profile,
                    )
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        (
            "agent_kind",
            "module_name",
            "factory_name",
            "function_name",
            "expected_default",
        ),
        AGENT_CASES,
        ids=[case[0] for case in AGENT_CASES],
    )
    async def test_bing_search_failures_raise_external_service_error(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_settings: None,
        agent_kind: str,
        module_name: str,
        factory_name: str,
        function_name: str,
        expected_default: Any,
    ) -> None:
        """Verify Bing search failures become typed service errors."""
        module = pytest.importorskip(module_name)
        agent_function = getattr(module, function_name)

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(
            side_effect=RuntimeError("Bing Search API error")
        )

        with patch(
            f"{module_name}.{factory_name}",
            return_value=mock_agent,
        ):
            with pytest.raises(ExternalServiceError):
                await agent_function(
                    *_build_agent_args(
                        agent_kind,
                        sample_customer_profile,
                    )
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        (
            "agent_kind",
            "module_name",
            "factory_name",
            "function_name",
            "expected_default",
        ),
        AGENT_CASES,
        ids=[case[0] for case in AGENT_CASES],
    )
    async def test_malformed_llm_responses_raise_external_service_error(
        self,
        sample_customer_profile: Dict[str, Any],
        mock_settings: None,
        agent_kind: str,
        module_name: str,
        factory_name: str,
        function_name: str,
        expected_default: Any,
    ) -> None:
        """Verify malformed LLM responses raise typed service errors."""
        module = pytest.importorskip(module_name)
        agent_function = getattr(module, function_name)

        mock_response = MagicMock()
        mock_response.text = "{not-valid-json"
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_response)

        with patch(
            f"{module_name}.{factory_name}",
            return_value=mock_agent,
        ):
            with pytest.raises(ExternalServiceError):
                await agent_function(
                    *_build_agent_args(
                        agent_kind,
                        sample_customer_profile,
                    )
                )
