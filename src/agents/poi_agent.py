"""POI Agent — Points of Interest Discovery.

This agent finds and recommends 5-8 specific attractions,
landmarks, or experiences for a destination. All recommendations
are grounded in web search results.
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
from src.api.models.itinerary import PointOfInterest
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the POI agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    prompt_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "prompts"
        / "poi-agent"
        / "system.md"
    )
    return prompt_path.read_text(encoding="utf-8")


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
        ValueError: If Azure OpenAI endpoint/deployment missing.
    """
    if not all(
        [
            settings.AZURE_OPENAI_ENDPOINT,
            settings.AZURE_OPENAI_DEPLOYMENT,
        ]
    ):
        raise ValueError(
            "Azure OpenAI not configured. Set "
            "AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_DEPLOYMENT."
        )

    credential = DefaultAzureCredential()

    client = AzureAIClient(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        credential=credential,
        deployment=settings.AZURE_OPENAI_DEPLOYMENT,
    )

    instructions = _load_system_prompt()

    agent = Agent(
        client=client,
        instructions=instructions,
        name="poi-agent",
        description="Points of interest discovery agent",
    )

    return agent


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
        settings: Application settings (optional, will load if
            None).

    Returns:
        List of 5-8 POIs. Returns empty list if insufficient web
        evidence.

    Raises:
        ValueError: If Azure OpenAI credentials not configured.
    """
    if settings is None:
        from src.config.settings import get_settings

        settings = get_settings()

    # Create agent
    agent = create_poi_agent(settings)

    # Build user prompt
    user_prompt = (
        f"Find points of interest for this destination:\n\n"
        f"Destination: {destination_name}, {country}\n"
        f"Travel dates: {travel_dates.start} to "
        f"{travel_dates.end}\n\n"
        f"Return 5-8 diverse attractions covering history, food, "
        f"nature, culture, and shopping."
    )

    logger.info(
        f"Requesting POIs for {destination_name} from POI Agent"
    )

    try:
        # Run agent
        response = await agent.run(user_prompt)

        # Parse response
        response_text = response.content.strip()

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
        pois_data = json.loads(response_text)

        # Validate and convert to PointOfInterest objects
        pois: List[PointOfInterest] = []
        for poi_data in pois_data:
            try:
                poi = PointOfInterest(**poi_data)
                pois.append(poi)
            except (KeyError, ValidationError) as e:
                logger.warning(f"Skipping invalid POI data: {e}")

        logger.info(
            f"POI Agent returned {len(pois)} POIs for "
            f"{destination_name}"
        )
        return pois

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent response as JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error running POI Agent: {e}")
        return []
