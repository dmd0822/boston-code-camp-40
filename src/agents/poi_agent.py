"""POI Agent — Points of Interest Discovery.

This agent finds and recommends 5-8 specific attractions,
landmarks, or experiences for a destination. All recommendations
are grounded in web search results.
"""

import logging
from typing import List, Optional

from agent_framework import Agent
from agent_framework_azure_ai import AzureAIClient
from azure.identity import DefaultAzureCredential
from pydantic import ValidationError

from src.agents.agent_utils import (
    load_system_prompt,
    parse_json_payload,
    run_agent_prompt,
)
from src.api.models.customer import TravelDates
from src.api.models.itinerary import PointOfInterest
from src.config.settings import Settings
from src.exceptions import ExternalServiceError, ServiceConfigurationError

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the POI agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    return load_system_prompt("poi-agent")


def create_poi_agent(settings: Settings) -> Agent:
    """Create and configure the POI Agent.

    Uses DefaultAzureCredential for authentication. Locally,
    run ``az login`` first. In Azure, managed identity is
    used automatically.

    Args:
        settings: Application settings with Azure OpenAI config.

    Returns:
        Configured Agent instance ready to find POIs.

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
        name="poi-agent",
        description="Points of interest discovery agent",
    )


async def find_points_of_interest(
    destination_name: str,
    country: str,
    travel_dates: TravelDates,
    settings: Optional[Settings] = None,
) -> List[PointOfInterest]:
    """Find points of interest for a destination.

    Args:
        destination_name: Name of the destination city/region.
        country: Country of the destination.
        travel_dates: Travel date range.
        settings: Application settings (optional, will load if None).

    Returns:
        List of 5-8 POIs.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is missing.
        ExternalServiceError: If the POI Agent response is invalid.
    """
    if settings is None:
        from src.config.settings import get_settings

        try:
            settings = get_settings()
        except ValidationError as exc:
            raise ServiceConfigurationError(
                "Application settings could not be loaded."
            ) from exc

    agent = create_poi_agent(settings)
    user_prompt = (
        f"Find points of interest for this destination:\n\n"
        f"Destination: {destination_name}, {country}\n"
        f"Travel dates: {travel_dates.start} to "
        f"{travel_dates.end}\n\n"
        f"Return 5-8 diverse attractions covering history, food, "
        f"nature, culture, and shopping."
    )

    logger.info("Requesting POIs for %s from POI Agent.", destination_name)
    response_text = await run_agent_prompt(
        agent=agent,
        user_prompt=user_prompt,
        agent_name="POI Agent",
        timeout_seconds=settings.AZURE_OPENAI_TIMEOUT_SECONDS,
        logger=logger,
    )
    pois_data = parse_json_payload(response_text, "POI Agent")

    if not isinstance(pois_data, list):
        logger.error(
            "POI Agent returned payload type %s.",
            type(pois_data).__name__,
        )
        raise ExternalServiceError(
            "POI Agent returned an invalid response format."
        )

    pois: List[PointOfInterest] = []
    for poi_data in pois_data:
        if not isinstance(poi_data, dict):
            logger.warning(
                "Skipping non-object POI payload: %r",
                poi_data,
            )
            continue

        try:
            pois.append(PointOfInterest(**poi_data))
        except (TypeError, ValidationError) as exc:
            logger.warning("Skipping invalid POI data: %s", exc)

    logger.info(
        "POI Agent returned %s POIs for %s.",
        len(pois),
        destination_name,
    )
    return pois
