"""Weather Agent — Historical Weather Forecasting.

This agent provides expected weather conditions for a destination
based on historical averages for the travel month. Returns None
if insufficient web evidence.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from agent_framework import Agent
from agent_framework_azure_ai import AzureAIClient
from azure.identity import DefaultAzureCredential
from pydantic import ValidationError

from src.api.models.customer import TravelDates
from src.api.models.itinerary import WeatherForecast
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the weather agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    prompt_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "prompts"
        / "weather-agent"
        / "system.md"
    )
    return prompt_path.read_text(encoding="utf-8")


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
        ValueError: If Azure OpenAI endpoint/deployment missing.
    """
    if not all(
        [
            settings.AZURE_AI_PROJECT_ENDPOINT,
            settings.AZURE_AI_MODEL_DEPLOYMENT_NAME,
        ]
    ):
        raise ValueError(
            "Azure AI Foundry not configured. Set "
            "AZURE_AI_PROJECT_ENDPOINT and "
            "AZURE_AI_MODEL_DEPLOYMENT_NAME."
        )

    credential = DefaultAzureCredential()

    client = AzureAIClient(
        project_endpoint=settings.AZURE_AI_PROJECT_ENDPOINT,
        credential=credential,
        model_deployment_name=settings.AZURE_AI_MODEL_DEPLOYMENT_NAME,
    )

    instructions = _load_system_prompt()

    agent = Agent(
        client=client,
        instructions=instructions,
        name="weather-agent",
        description="Historical weather forecasting agent",
    )

    return agent


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
        settings: Application settings (optional, will load if
            None).

    Returns:
        WeatherForecast with historical averages, or None if
        insufficient web evidence.

    Raises:
        ValueError: If Azure OpenAI credentials not configured.
    """
    if settings is None:
        from src.config.settings import get_settings

        settings = get_settings()

    # Create agent
    agent = create_weather_agent(settings)

    # Extract month for weather query
    month_name = travel_dates.start.strftime("%B")

    # Build user prompt
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
        f"Requesting weather forecast for {destination_name} "
        f"from Weather Agent"
    )

    try:
        # Run agent
        response = await agent.run(user_prompt)

        # Parse response
        response_text = response.text.strip()

        # Try to extract JSON from markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        # Handle null response
        if response_text.lower() == "null":
            logger.info(
                f"Weather Agent returned null for "
                f"{destination_name}"
            )
            return None

        # Parse JSON
        weather_data = json.loads(response_text)

        # Validate and convert to WeatherForecast
        try:
            forecast = WeatherForecast(**weather_data)
            logger.info(
                f"Weather Agent returned forecast for "
                f"{destination_name}"
            )
            return forecast
        except (KeyError, ValidationError) as e:
            logger.warning(
                f"Invalid weather forecast data: {e}"
            )
            return None

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error running Weather Agent: {e}")
        return None
