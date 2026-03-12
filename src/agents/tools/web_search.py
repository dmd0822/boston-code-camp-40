"""Bing Web Search tool for agent grounding.

This tool wraps the Bing Web Search API to provide factual
grounding for all agents. It handles API errors gracefully and
returns structured search results.

Bing Search is optional — when credentials are absent the tool
returns an empty list so agents can still function without it.
"""

import logging
import os
from typing import Any, Dict, List

import httpx
from agent_framework import tool

logger = logging.getLogger(__name__)


class SearchResult(Dict[str, Any]):
    """Search result with title, URL, and snippet."""

    pass


@tool
async def search_web(
    query: str,
    max_results: int = 5,
) -> List[SearchResult]:
    """Search the web using Bing Web Search API.

    This tool provides factual grounding for agents. It queries
    the Bing API and returns structured results that agents can
    cite in their responses.

    Credentials are read from environment variables so the tool
    works independently of the application Settings model.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of search results, each with title, url, and snippet.
        Returns empty list if API credentials are missing or on
        error.
    """
    api_key = os.environ.get("BING_SEARCH_API_KEY", "")
    endpoint = os.environ.get(
        "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com/"
    )

    if not api_key:
        logger.warning(
            "Bing Search API credentials not configured. "
            "Returning empty results."
        )
        return []

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {
        "q": query,
        "count": max_results,
        "mkt": "en-US",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{endpoint.rstrip('/')}/v7.0/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()

            data = response.json()
            web_pages = data.get("webPages", {}).get("value", [])

            results: List[SearchResult] = []
            for page in web_pages[:max_results]:
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
                f"Web search for '{query}' returned "
                f"{len(results)} results"
            )
            return results

    except httpx.TimeoutException:
        logger.error(f"Timeout searching for '{query}'")
        return []
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            logger.error(
                "Invalid Bing Search API key. Check "
                "BING_SEARCH_API_KEY."
            )
        elif e.response.status_code == 429:
            logger.error("Bing Search API rate limit exceeded.")
        else:
            logger.error(
                f"HTTP error {e.response.status_code} "
                f"searching for '{query}'"
            )
        return []
    except Exception as e:
        logger.error(
            f"Unexpected error searching for '{query}': {e}"
        )
        return []
