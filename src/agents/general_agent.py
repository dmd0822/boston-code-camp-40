"""General Agent — Destination Matching.

This agent analyzes customer profiles and recommends 3-4
destinations based on interests, budget, travel dates, and
departure city. All recommendations are grounded in web search
results.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from agent_framework import Agent
from agent_framework_azure_ai import AzureAIClient
from pydantic import ValidationError

from src.api.models.customer import CustomerProfile
from src.api.models.itinerary import Destination
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the general agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    prompt_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "prompts"
        / "general-agent"
        / "system.md"
    )
    return prompt_path.read_text(encoding="utf-8")


def create_general_agent(settings: Settings) -> Agent:
    """Create and configure the General Agent.

    Args:
        settings: Application settings with Azure OpenAI config.

    Returns:
        Configured Agent instance ready to recommend destinations.

    Raises:
        ValueError: If Azure OpenAI credentials are not configured.
    """
    if not all(
        [
            settings.AZURE_OPENAI_ENDPOINT,
            settings.AZURE_OPENAI_API_KEY,
            settings.AZURE_OPENAI_DEPLOYMENT,
        ]
    ):
        raise ValueError(
            "Azure OpenAI credentials not configured. Set "
            "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and "
            "AZURE_OPENAI_DEPLOYMENT."
        )

    # Create Azure OpenAI client
    client = AzureAIClient(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        deployment=settings.AZURE_OPENAI_DEPLOYMENT,
    )

    # Load system prompt
    instructions = _load_system_prompt()

    # Import search tool
    from src.agents.tools.web_search import search_web

    # Create agent with search tool
    agent = Agent(
        client=client,
        instructions=instructions,
        name="general-agent",
        description="Destination matching agent",
        tools=[search_web],
    )

    return agent


async def recommend_destinations(
    profile: CustomerProfile, settings: Optional[Settings] = None
) -> List[Destination]:
    """Recommend destinations based on customer profile.

    Args:
        profile: Customer's travel preferences and constraints.
        settings: Application settings (optional, will load if None).

    Returns:
        List of 3-4 recommended destinations with rationale.
        Returns empty list if insufficient web evidence.

    Raises:
        ValueError: If Azure OpenAI credentials not configured.
    """
    if settings is None:
        from src.config.settings import get_settings

        settings = get_settings()

    # Create agent
    agent = create_general_agent(settings)

    # Build user prompt from profile
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

    logger.info(f"Requesting destinations from General Agent")

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
        destinations_data = json.loads(response_text)

        # Validate and convert to Destination objects
        destinations: List[Destination] = []
        for dest_data in destinations_data:
            try:
                destination = Destination(
                    name=dest_data["name"],
                    country=dest_data["country"],
                    rationale=dest_data["rationale"],
                )
                destinations.append(destination)
            except (KeyError, ValidationError) as e:
                logger.warning(
                    f"Skipping invalid destination data: {e}"
                )

        logger.info(
            f"General Agent returned {len(destinations)} "
            f"destinations"
        )
        return destinations

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent response as JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error running General Agent: {e}")
        return []
