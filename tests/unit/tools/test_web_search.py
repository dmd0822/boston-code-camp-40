"""Unit tests for the Bing Web Search tool.

Tests the search_web function that wraps the Bing Web Search API.
All tests use mocked HTTP responses — no real API calls.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from src.config.settings import Settings


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_bing_api_response() -> Dict[str, Any]:
    """Return a realistic Bing Search API response structure."""
    return {
        "webPages": {
            "value": [
                {
                    "name": "Lisbon Travel Guide",
                    "url": "https://example.com/lisbon",
                    "snippet": "Explore Lisbon's history and culture.",
                },
                {
                    "name": "Best Restaurants in Lisbon",
                    "url": "https://example.com/restaurants",
                    "snippet": "Top dining spots in Portugal's capital.",
                },
            ],
        },
    }


@pytest.fixture()
def mock_empty_bing_response() -> Dict[str, Any]:
    """Return a Bing API response with no results."""
    return {"webPages": {"value": []}}


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestWebSearchTool:
    """Test suite for the search_web tool."""

    @pytest.mark.asyncio
    async def test_successful_search_returns_structured_results(
        self,
        mock_settings: None,
        mock_bing_api_response: Dict[str, Any],
    ) -> None:
        """Verify search_web returns list of dicts with required keys.

        Each result must have: title, url, snippet.
        """
        pytest.importorskip("src.agents.tools.web_search")
        from src.agents.tools.web_search import search_web

        settings = Settings()

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_bing_api_response)
            mock_response.raise_for_status = Mock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_client

            results = await search_web("Lisbon travel", settings)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(
                "title" in r and "url" in r and "snippet" in r
                for r in results
            )
            assert results[0]["title"] == "Lisbon Travel Guide"
            assert results[0]["url"] == "https://example.com/lisbon"

    @pytest.mark.asyncio
    async def test_handles_missing_api_key_gracefully(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Verify search_web returns empty list when API key missing.

        Without a valid API key, the tool should return empty list
        rather than make invalid requests.
        """
        pytest.importorskip("src.agents.tools.web_search")
        from src.agents.tools.web_search import search_web

        monkeypatch.setenv("BING_SEARCH_API_KEY", "")
        monkeypatch.setenv(
            "BING_SEARCH_ENDPOINT",
            "https://api.bing.microsoft.com/",
        )
        settings = Settings()

        # Should return empty list when credentials missing
        results = await search_web("test query", settings)
        assert results == []

    @pytest.mark.asyncio
    async def test_handles_api_timeout(
        self, mock_settings: None
    ) -> None:
        """Verify search_web handles network timeout errors.

        Should return empty list, not crash.
        """
        pytest.importorskip("src.agents.tools.web_search")
        from src.agents.tools.web_search import search_web

        settings = Settings()

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_client

            results = await search_web("test query", settings)
            assert results == []

    @pytest.mark.asyncio
    async def test_handles_empty_search_results(
        self,
        mock_settings: None,
        mock_empty_bing_response: Dict[str, Any],
    ) -> None:
        """Verify search_web returns empty list when no results found.

        Should not raise an exception for valid queries with no
        matching content.
        """
        pytest.importorskip("src.agents.tools.web_search")
        from src.agents.tools.web_search import search_web

        settings = Settings()

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_empty_bing_response)
            mock_response.raise_for_status = Mock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_client

            results = await search_web("xyznonexistentquery123", settings)

            assert results == []

    @pytest.mark.asyncio
    async def test_handles_http_error_responses(
        self, mock_settings: None
    ) -> None:
        """Verify search_web handles HTTP errors (429, 500, etc).

        API rate limits and server errors should be caught and
        handled gracefully.
        """
        pytest.importorskip("src.agents.tools.web_search")
        from src.agents.tools.web_search import search_web

        settings = Settings()

        # Test 429 Rate Limit
        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.raise_for_status = Mock(
                side_effect=httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=Mock(),
                    response=mock_response,
                )
            )

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_client

            results = await search_web("test query", settings)
            assert results == []

    @pytest.mark.asyncio
    async def test_validates_result_structure(
        self,
        mock_settings: None,
        mock_bing_api_response: Dict[str, Any],
    ) -> None:
        """Verify each result has required fields: title, url, snippet.

        The contract guarantees downstream agents can rely on these
        fields being present.
        """
        pytest.importorskip("src.agents.tools.web_search")
        from src.agents.tools.web_search import search_web

        settings = Settings()

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_bing_api_response)
            mock_response.raise_for_status = Mock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_client

            results = await search_web("Lisbon", settings)

            for result in results:
                assert "title" in result, "Missing 'title' field"
                assert "url" in result, "Missing 'url' field"
                assert "snippet" in result, "Missing 'snippet' field"
                assert isinstance(result["title"], str)
                assert isinstance(result["url"], str)
                assert isinstance(result["snippet"], str)
