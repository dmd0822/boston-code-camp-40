"""General Agent — Destination Matching.

This agent analyzes customer profiles and recommends 3-4
destinations based on interests, budget, travel dates, and
departure city. All recommendations are grounded in web search
results.
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
from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import Destination
from src.config.settings import Settings
from src.exceptions import ExternalServiceError, ServiceConfigurationError

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the general agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    return load_system_prompt("general-agent")


def create_general_agent(settings: Settings) -> Agent:
    """Create and configure the General Agent.

    Uses DefaultAzureCredential for authentication. Locally,
    run ``az login`` first. In Azure, managed identity is
    used automatically.

    Args:
        settings: Application settings with Azure OpenAI config.

    Returns:
        Configured Agent instance ready to recommend destinations.

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
        name="general-agent",
        description="Destination matching agent",
    )


async def recommend_destinations(
    profile: CustomerProfile,
    settings: Optional[Settings] = None,
) -> List[Destination]:
    """Recommend destinations based on customer profile.

    Args:
        profile: Customer's travel preferences and constraints.
        settings: Application settings (optional, will load if None).

    Returns:
        List of at least 3 recommended destinations with rationale.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is missing.
        ExternalServiceError: If the General Agent response is invalid
            or returns fewer than 3 destinations.
    """
    if settings is None:
        from src.config.settings import get_settings

        try:
            settings = get_settings()
        except ValidationError as exc:
            raise ServiceConfigurationError(
                "Application settings could not be loaded."
            ) from exc

    agent = create_general_agent(settings)
    user_prompt = (
        f"Find destinations for this customer profile:\n\n"
        f"Interests: {', '.join(profile.interests)}\n"
        f"Budget: {profile.budget}\n"
        f"Travel dates: {profile.travel_dates.start} to "
        f"{profile.travel_dates.end}\n"
        f"Party size: {profile.party_size}\n"
        f"Departure city: {profile.departure_city}\n"
    )

    if profile.notes:
        user_prompt += f"Notes: {profile.notes}\n"

    logger.info("Requesting destinations from General Agent.")
    response_text = await run_agent_prompt(
        agent=agent,
        user_prompt=user_prompt,
        agent_name="General Agent",
        timeout_seconds=settings.AZURE_OPENAI_TIMEOUT_SECONDS,
        logger=logger,
    )
    destinations_data = parse_json_payload(response_text, "General Agent")

    if not isinstance(destinations_data, list):
        logger.error(
            "General Agent returned payload type %s.",
            type(destinations_data).__name__,
        )
        raise ExternalServiceError(
            "General Agent returned an invalid response format."
        )

    destinations: List[Destination] = []
    for dest_data in destinations_data:
        if not isinstance(dest_data, dict):
            logger.warning(
                "Skipping non-object destination payload: %r",
                dest_data,
            )
            continue

        try:
            destination = Destination(
                name=dest_data["name"],
                country=dest_data["country"],
                rationale=dest_data["rationale"],
            )
            destinations.append(destination)
        except (KeyError, TypeError, ValidationError) as exc:
            logger.warning("Skipping invalid destination data: %s", exc)

    logger.info(
        "General Agent returned %s destinations.",
        len(destinations),
    )

    if len(destinations) < 3:
        logger.error(
            "General Agent returned only %s destinations (minimum 3 "
            "required).",
            len(destinations),
        )
        raise ExternalServiceError(
            f"General Agent returned {len(destinations)} destinations, "
            "but at least 3 are required. The system cannot generate "
            "a complete itinerary with insufficient destinations."
        )

    return destinations
