"""Event Agent — Festival and Special Event Discovery.

This agent finds festivals, fairs, concerts, or other time-
bounded events happening at a destination during the travel
window. Returns empty list if no events match the dates.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from agent_framework import Agent
from agent_framework_azure_ai import AzureAIClient
from azure.identity import DefaultAzureCredential
from pydantic import ValidationError

from src.api.models.customer import TravelDates
from src.api.models.itinerary import Event
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the event agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    prompt_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "prompts"
        / "event-agent"
        / "system.md"
    )
    return prompt_path.read_text(encoding="utf-8")


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
        name="event-agent",
        description="Event and festival discovery agent",
    )

    return agent


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
        settings: Application settings (optional, will load if
            None).

    Returns:
        List of events overlapping the travel window. Returns
        empty list if no events found (this is normal and
        acceptable).

    Raises:
        ValueError: If Azure OpenAI credentials not configured.
    """
    if settings is None:
        from src.config.settings import get_settings

        settings = get_settings()

    # Create agent
    agent = create_event_agent(settings)

    # Build user prompt
    user_prompt = (
        f"Find events for this destination and date range:\n\n"
        f"Destination: {destination_name}, {country}\n"
        f"Travel dates: {travel_dates.start} to "
        f"{travel_dates.end}\n\n"
        f"Only return events that overlap with these dates. "
        f"Return an empty array if no events match."
    )

    logger.info(
        f"Requesting events for {destination_name} from Event "
        f"Agent"
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

        # Parse JSON
        events_data = json.loads(response_text)

        # Validate and convert to Event objects
        events: List[Event] = []
        for event_data in events_data:
            try:
                event = Event(**event_data)
                events.append(event)
            except (KeyError, ValidationError) as e:
                logger.warning(
                    f"Skipping invalid event data: {e}"
                )

        logger.info(
            f"Event Agent returned {len(events)} events for "
            f"{destination_name}"
        )
        return events

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent response as JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error running Event Agent: {e}")
        return []
