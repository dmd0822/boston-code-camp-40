"""Event Agent — Festival and Special Event Discovery.

This agent finds festivals, fairs, concerts, or other time-
bounded events happening at a destination during the travel
window. Returns empty list if no events match the dates.
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
from src.api.models.itinerary import Event
from src.config.settings import Settings
from src.exceptions import ExternalServiceError, ServiceConfigurationError

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the event agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    return load_system_prompt("event-agent")


def create_event_agent(settings: Settings) -> Agent:
    """Create and configure the Event Agent.

    Uses DefaultAzureCredential for authentication. Locally,
    run ``az login`` first. In Azure, managed identity is
    used automatically.

    Args:
        settings: Application settings with Azure OpenAI config.

    Returns:
        Configured Agent instance ready to find events.

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
        name="event-agent",
        description="Event and festival discovery agent",
    )


async def find_events(
    destination_name: str,
    country: str,
    travel_dates: TravelDates,
    settings: Optional[Settings] = None,
) -> List[Event]:
    """Find events happening during the travel window.

    Args:
        destination_name: Name of the destination city/region.
        country: Country of the destination.
        travel_dates: Travel date range.
        settings: Application settings (optional, will load if None).

    Returns:
        List of events overlapping the travel window.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is missing.
        ExternalServiceError: If the Event Agent response is invalid.
    """
    if settings is None:
        from src.config.settings import get_settings

        try:
            settings = get_settings()
        except ValidationError as exc:
            raise ServiceConfigurationError(
                "Application settings could not be loaded."
            ) from exc

    agent = create_event_agent(settings)
    user_prompt = (
        f"Find events for this destination and date range:\n\n"
        f"Destination: {destination_name}, {country}\n"
        f"Travel dates: {travel_dates.start} to "
        f"{travel_dates.end}\n\n"
        f"Only return events that overlap with these dates. "
        f"Return an empty array if no events match."
    )

    logger.info(
        "Requesting events for %s from Event Agent.",
        destination_name,
    )
    response_text = await run_agent_prompt(
        agent=agent,
        user_prompt=user_prompt,
        agent_name="Event Agent",
        timeout_seconds=settings.AZURE_OPENAI_TIMEOUT_SECONDS,
        logger=logger,
    )
    events_data = parse_json_payload(response_text, "Event Agent")

    if not isinstance(events_data, list):
        logger.error(
            "Event Agent returned payload type %s.",
            type(events_data).__name__,
        )
        raise ExternalServiceError(
            "Event Agent returned an invalid response format."
        )

    events: List[Event] = []
    for event_data in events_data:
        if not isinstance(event_data, dict):
            logger.warning(
                "Skipping non-object event payload: %r",
                event_data,
            )
            continue

        try:
            events.append(Event(**event_data))
        except (TypeError, ValidationError) as exc:
            logger.warning("Skipping invalid event data: %s", exc)

    logger.info(
        "Event Agent returned %s events for %s.",
        len(events),
        destination_name,
    )
    return events
