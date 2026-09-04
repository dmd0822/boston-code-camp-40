"""Travel Advisory Agent — State Department Advisory Lookup.

This agent checks current U.S. State Department travel
advisories for a destination. Returns the advisory level (1-4),
summary, and specific warnings grounded in web search results.
"""

import logging
from typing import Any, Optional

from azure.identity import DefaultAzureCredential
from pydantic import ValidationError

# agent-framework packages are imported here at module level so that
# patch("src.agents.travel_advisory_agent.AzureAIClient") works in
# unit tests. The try/except prevents an ImportError at collection time
# when the installed versions of agent-framework-azure-ai and
# agent-framework-core are incompatible; the error surfaces only when
# an agent is actually created at runtime.
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
from src.api.models.itinerary import TravelAdvisory
from src.config.settings import Settings
from src.exceptions import (
    ExternalServiceError,
    ServiceConfigurationError,
)

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    """Load the travel advisory agent system prompt from file.

    Returns:
        System prompt as a string.
    """
    return load_system_prompt("travel-advisory-agent")


def create_travel_advisory_agent(settings: Settings) -> Agent:
    """Create and configure the Travel Advisory Agent.

    Uses DefaultAzureCredential for authentication. Locally,
    run ``az login`` first. In Azure, managed identity is
    used automatically.

    Args:
        settings: Application settings with Azure OpenAI config.

    Returns:
        Configured Agent instance ready to look up advisories.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is
            invalid.
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
        name="travel-advisory-agent",
        description="State Department travel advisory agent",
    )


async def get_travel_advisory(
    destination_name: str,
    country: str,
    travel_dates: TravelDates,
    settings: Optional[Settings] = None,
) -> Optional[TravelAdvisory]:
    """Get the current travel advisory for a destination.

    Args:
        destination_name: Name of the destination city/region.
        country: Country of the destination.
        travel_dates: Travel date range.
        settings: Application settings (optional, loads if None).

    Returns:
        TravelAdvisory with level, warnings, and source, or
        None if the agent returns explicit ``null``.

    Raises:
        ServiceConfigurationError: If Azure OpenAI config is
            missing.
        ExternalServiceError: If the Travel Advisory Agent
            response is invalid.
    """
    if settings is None:
        from src.config.settings import get_settings

        try:
            settings = get_settings()
        except ValidationError as exc:
            raise ServiceConfigurationError(
                "Application settings could not be loaded."
            ) from exc

    agent = create_travel_advisory_agent(settings)
    user_prompt = (
        f"Find the current U.S. State Department travel "
        f"advisory for this destination:\n\n"
        f"Destination: {destination_name}, {country}\n"
        f"Travel dates: {travel_dates.start} to "
        f"{travel_dates.end}\n\n"
        f"Return the advisory level (1-4), a summary, "
        f"specific warnings, and source URL. "
        f"Return null if no advisory can be found."
    )

    logger.info(
        "Requesting travel advisory for %s, %s "
        "from Travel Advisory Agent.",
        destination_name,
        country,
    )
    response_text = await run_agent_prompt(
        agent=agent,
        user_prompt=user_prompt,
        agent_name="Travel Advisory Agent",
        timeout_seconds=settings.AZURE_OPENAI_TIMEOUT_SECONDS,
        logger=logger,
    )

    if response_text.lower() == "null":
        logger.info(
            "Travel Advisory Agent returned null for %s, %s.",
            destination_name,
            country,
        )
        return None

    advisory_data = parse_json_payload(
        response_text,
        "Travel Advisory Agent",
    )
    if not isinstance(advisory_data, dict):
        logger.error(
            "Travel Advisory Agent returned payload type %s.",
            type(advisory_data).__name__,
        )
        raise ExternalServiceError(
            "Travel Advisory Agent returned an invalid "
            "response format."
        )

    try:
        advisory = TravelAdvisory(**advisory_data)
    except (TypeError, ValidationError) as exc:
        logger.warning(
            "Invalid travel advisory data: %s",
            exc,
        )
        return None

    logger.info(
        "Travel Advisory Agent returned level %s advisory "
        "for %s, %s.",
        advisory.advisory_level,
        destination_name,
        country,
    )
    return advisory
