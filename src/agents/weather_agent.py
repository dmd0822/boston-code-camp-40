"""Weather Agent — Historical Weather Forecasting.

This agent provides expected weather conditions for a destination
based on historical averages for the travel month. Returns None
if insufficient web evidence.
"""

import logging
from typing import Any, Optional

from azure.identity import DefaultAzureCredential
from pydantic import ValidationError

# agent-framework packages are imported here at module level so that
# patch("src.agents.weather_agent.AzureAIClient") works in unit tests.
# The try/except prevents an ImportError at collection time when the
# installed versions of agent-framework-azure-ai and agent-framework-core
# are incompatible; the error surfaces only when an agent is actually
# created at runtime.
try:
    from agent_framework import Agent
    from agent_framework_azure_ai import AzureAIClient
except ImportError:  # pragma: no cover
    Agent: Any = None  # type: ignore[assignment]
    AzureAIClient: Any = None  # type: ignore[assignment]

from src.agents.agent_utils import (
    load_system_prompt,
    parse_json_payload,
    run_agent_prompt,
)
from src.api.models.customer import TravelDates
from src.api.models.itinerary import WeatherForecast
from src.config.settings import Settings
from src.exceptions import ExternalServiceError, ServiceConfigurationError

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the weather agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    return load_system_prompt("weather-agent")


def create_weather_agent(settings: Settings) -> Agent:
    """Create and configure the Weather Agent.

    Uses DefaultAzureCredential for authentication. Locally,
    run ``az login`` first. In Azure, managed identity is
    used automatically.

    Args:
        settings: Application settings with Azure OpenAI config.

    Returns:
        Configured Agent instance ready to forecast weather.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is invalid.
    """
    if not all(
        [
            settings.AZURE_AI_PROJECT_ENDPOINT,
            settings.AZURE_AI_MODEL_DEPLOYMENT_NAME,
        ]
    ):
        raise ServiceConfigurationError(
            "Azure AI Foundry is not configured. Set "
            "AZURE_AI_PROJECT_ENDPOINT and "
            "AZURE_AI_MODEL_DEPLOYMENT_NAME."
        )

    credential = DefaultAzureCredential()

    try:
        client = AzureAIClient(
            project_endpoint=settings.AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
            model_deployment_name=(
                settings.AZURE_AI_MODEL_DEPLOYMENT_NAME
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ServiceConfigurationError(
            "Azure OpenAI client could not be initialized."
        ) from exc

    instructions = _load_system_prompt()
    return Agent(
        client=client,
        instructions=instructions,
        name="weather-agent",
        description="Historical weather forecasting agent",
    )


async def get_weather_forecast(
    destination_name: str,
    country: str,
    travel_dates: TravelDates,
    settings: Optional[Settings] = None,
) -> Optional[WeatherForecast]:
    """Get historical weather forecast for a destination.

    Args:
        destination_name: Name of the destination city/region.
        country: Country of the destination.
        travel_dates: Travel date range.
        settings: Application settings (optional, will load if None).

    Returns:
        WeatherForecast with historical averages, or None if the
        agent returns explicit ``null``.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is missing.
        ExternalServiceError: If the Weather Agent response is invalid.
    """
    if settings is None:
        from src.config.settings import get_settings

        try:
            settings = get_settings()
        except ValidationError as exc:
            raise ServiceConfigurationError(
                "Application settings could not be loaded."
            ) from exc

    agent = create_weather_agent(settings)
    month_name = travel_dates.start.strftime("%B")
    user_prompt = (
        f"Provide historical weather forecast for:\n\n"
        f"Destination: {destination_name}, {country}\n"
        f"Month: {month_name}\n"
        f"Travel dates: {travel_dates.start} to "
        f"{travel_dates.end}\n\n"
        f"Return historical averages (NOT real-time forecast). "
        f"Return null if insufficient data."
    )

    logger.info(
        "Requesting weather forecast for %s from Weather Agent.",
        destination_name,
    )
    response_text = await run_agent_prompt(
        agent=agent,
        user_prompt=user_prompt,
        agent_name="Weather Agent",
        timeout_seconds=settings.AZURE_OPENAI_TIMEOUT_SECONDS,
        logger=logger,
    )

    if response_text.lower() == "null":
        logger.info(
            "Weather Agent returned null for %s.",
            destination_name,
        )
        return None

    weather_data = parse_json_payload(response_text, "Weather Agent")
    if not isinstance(weather_data, dict):
        logger.error(
            "Weather Agent returned payload type %s.",
            type(weather_data).__name__,
        )
        raise ExternalServiceError(
            "Weather Agent returned an invalid response format."
        )

    try:
        forecast = WeatherForecast(**weather_data)
    except (TypeError, ValidationError) as exc:
        logger.warning("Invalid weather forecast data: %s", exc)
        return None

    logger.info(
        "Weather Agent returned forecast for %s.",
        destination_name,
    )
    return forecast
