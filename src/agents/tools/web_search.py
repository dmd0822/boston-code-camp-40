"""Bing Web Search tool for agent grounding.

This tool wraps the Bing Web Search API to provide factual
grounding for all agents. It handles API errors gracefully and
returns structured search results.

Bing Search is optional — when credentials are absent the tool
returns an empty list so agents can still function without it.
"""

import logging
from typing import Any, Dict, List

import httpx
from agent_framework import tool
from pydantic import ValidationError

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class SearchResult(Dict[str, Any]):
    """Search result with title, URL, and snippet."""

    pass


def _load_search_settings() -> Settings:
    """Load uncached settings so env overrides apply immediately.

    Returns:
        Settings: Fresh settings instance for the current call.

    Raises:
        ValidationError: If the environment configuration is invalid.
    """
    return Settings()


@tool
async def search_web(
    query: str,
    max_results: int = 5,
) -> List[SearchResult]:
    """Search the web using Bing Web Search API.

    This tool provides factual grounding for agents. It queries
    the Bing API and returns structured results that agents can
    cite in their responses.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of search results, each with title, url, and snippet.
        Returns empty list if API credentials are missing or on
        error.
    """
    normalized_query = query.strip()
    if not normalized_query:
        logger.warning("Received empty Bing search query.")
        return []

    limited_results = max(1, min(max_results, 10))

    try:
        settings = _load_search_settings()
    except ValidationError:
        logger.error("Bing Search settings are invalid.", exc_info=True)
        return []

    api_key = settings.BING_SEARCH_API_KEY or ""
    endpoint = settings.BING_SEARCH_ENDPOINT.rstrip("/")
    timeout_seconds = settings.BING_SEARCH_TIMEOUT_SECONDS

    if not api_key:
        logger.warning(
            "Bing Search API credentials not configured. Returning "
            "empty results."
        )
        return []

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {
        "q": normalized_query,
        "count": limited_results,
        "mkt": "en-US",
    }
    timeout = httpx.Timeout(timeout_seconds)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{endpoint}/v7.0/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(
            "Bing Search timed out for query '%s'.",
            normalized_query,
            exc_info=True,
        )
        return []
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        if status_code == 401:
            logger.error(
                "Invalid Bing Search API key. Check "
                "BING_SEARCH_API_KEY."
            )
        elif status_code == 429:
            logger.error("Bing Search API rate limit exceeded.")
        else:
            logger.error(
                "Bing Search HTTP error %s for query '%s'.",
                status_code,
                normalized_query,
                exc_info=True,
            )
        return []
    except httpx.RequestError as exc:
        logger.error(
            "Bing Search request failed for query '%s': %s",
            normalized_query,
            exc,
            exc_info=True,
        )
        return []

    try:
        data = response.json()
    except ValueError:
        logger.error(
            "Bing Search returned invalid JSON for query '%s'.",
            normalized_query,
            exc_info=True,
        )
        return []

    web_pages = data.get("webPages", {}).get("value", [])
    results: List[SearchResult] = []
    for page in web_pages[:limited_results]:
        results.append(
            SearchResult(
                {
                    "title": page.get("name", ""),
                    "url": page.get("url", ""),
                    "snippet": page.get("snippet", ""),
                }
            )
        )

    logger.info(
        "Web search for '%s' returned %s results.",
        normalized_query,
        len(results),
    )
    return results
