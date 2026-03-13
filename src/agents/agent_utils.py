"""Shared helpers for agent prompt loading and execution."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
    ServiceResponseError,
)

from src.exceptions import (
    ExternalServiceError,
    ExternalServiceTimeoutError,
    ServiceConfigurationError,
)

PROMPTS_ROOT = Path(__file__).parent.parent.parent / "data" / "prompts"


def load_system_prompt(prompt_name: str) -> str:
    """Load a system prompt from the prompts directory.

    Args:
        prompt_name: Directory name under ``data/prompts``.

    Returns:
        str: Prompt contents.

    Raises:
        ServiceConfigurationError: If the prompt file cannot be read.
    """
    prompt_path = PROMPTS_ROOT / prompt_name / "system.md"
    try:
        return prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ServiceConfigurationError(
            f"System prompt '{prompt_name}' could not be loaded."
        ) from exc


async def run_agent_prompt(
    *,
    agent: Any,
    user_prompt: str,
    agent_name: str,
    timeout_seconds: float,
    logger: logging.Logger,
) -> str:
    """Run an agent with timeout protection and response validation.

    Args:
        agent: Configured agent instance.
        user_prompt: Prompt sent to the agent.
        agent_name: Human-friendly agent name for logs and errors.
        timeout_seconds: Maximum allowed execution time.
        logger: Logger for structured diagnostics.

    Returns:
        str: Cleaned response text with markdown fences removed.

    Raises:
        ExternalServiceTimeoutError: If Azure OpenAI times out.
        ServiceConfigurationError: If authentication fails.
        ExternalServiceError: If execution or response parsing fails.
    """
    try:
        async with asyncio.timeout(timeout_seconds):
            response = await agent.run(user_prompt)
    except TimeoutError as exc:
        logger.error(
            "%s timed out after %.1f seconds.",
            agent_name,
            timeout_seconds,
            exc_info=True,
        )
        raise ExternalServiceTimeoutError(
            f"{agent_name} timed out while contacting Azure OpenAI."
        ) from exc
    except ClientAuthenticationError as exc:
        logger.error(
            "%s authentication failed.",
            agent_name,
            exc_info=True,
        )
        raise ServiceConfigurationError(
            "Azure OpenAI authentication failed. Check service "
            "identity and configuration."
        ) from exc
    except (
        ServiceRequestError,
        ServiceResponseError,
        HttpResponseError,
    ) as exc:
        logger.error(
            "%s request to Azure OpenAI failed.",
            agent_name,
            exc_info=True,
        )
        raise ExternalServiceError(
            f"{agent_name} could not reach Azure OpenAI."
        ) from exc
    except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
        logger.error(
            "%s execution failed.",
            agent_name,
            exc_info=True,
        )
        raise ExternalServiceError(
            f"{agent_name} failed to generate a response."
        ) from exc

    response_text = getattr(response, "text", None)
    if not isinstance(response_text, str) or not response_text.strip():
        logger.error("%s returned an empty response.", agent_name)
        raise ExternalServiceError(
            f"{agent_name} returned an empty response."
        )

    return extract_json_payload(response_text.strip())


def extract_json_payload(response_text: str) -> str:
    """Remove optional markdown fences from an agent response.

    Args:
        response_text: Raw agent response text.

    Returns:
        str: Clean JSON payload string.
    """
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        return response_text[start:end].strip()

    if "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        return response_text[start:end].strip()

    return response_text


def parse_json_payload(payload: str, agent_name: str) -> Any:
    """Parse JSON returned by an agent.

    Args:
        payload: JSON text extracted from the response.
        agent_name: Agent name for diagnostics.

    Returns:
        Any: Parsed JSON object.

    Raises:
        ExternalServiceError: If the payload is not valid JSON.
    """
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ExternalServiceError(
            f"{agent_name} returned invalid JSON."
        ) from exc
