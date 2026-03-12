"""Shared pytest fixtures for the Travel Agent test suite.

Provides reusable test data aligned with the Pydantic model
schemas defined in ``src/api/models/``.  Every fixture returns
a plain ``dict`` (or object) so tests can mutate copies freely.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import date, datetime, timezone
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest


# ------------------------------------------------------------------
# Customer fixtures
# ------------------------------------------------------------------

@pytest.fixture()
def sample_travel_dates() -> Dict[str, str]:
    """Return a valid TravelDates dict (start < end)."""
    return {
        "start": "2026-06-15",
        "end": "2026-06-25",
    }


@pytest.fixture()
def sample_customer_profile(
    sample_travel_dates: Dict[str, str],
) -> Dict[str, Any]:
    """Return a fully-populated CustomerProfile dict.

    Includes all required and optional fields so tests can
    selectively remove keys to verify validation.
    """
    return {
        "interests": ["history", "food", "hiking"],
        "budget": "moderate",
        "travel_dates": deepcopy(sample_travel_dates),
        "party_size": 2,
        "departure_city": "Boston",
        "notes": "Prefer warm weather, no long flights",
    }


# ------------------------------------------------------------------
# Destination / sub-model fixtures
# ------------------------------------------------------------------

@pytest.fixture()
def sample_point_of_interest() -> Dict[str, Any]:
    """Return a valid PointOfInterest dict with a source URL."""
    return {
        "name": "Belém Tower",
        "description": "UNESCO World Heritage Site and "
        "iconic Lisbon landmark.",
        "category": "history",
        "visit_duration_hours": 1.5,
        "source_url": "https://example.com/belem-tower",
    }


@pytest.fixture()
def sample_event() -> Dict[str, Any]:
    """Return a valid Event dict with dates and source URL."""
    return {
        "name": "Festa de Santo António",
        "dates": {
            "start": "2026-06-12",
            "end": "2026-06-13",
        },
        "description": (
            "Lisbon's biggest street festival with "
            "parades and sardine grills."
        ),
        "venue": "Alfama district",
        "source_url": "https://example.com/santo-antonio",
    }


@pytest.fixture()
def sample_weather_forecast() -> Dict[str, Any]:
    """Return a valid WeatherForecast dict."""
    return {
        "avg_high_celsius": 27,
        "avg_low_celsius": 17,
        "precipitation_chance": "low",
        "clothing_suggestion": (
            "Light layers, comfortable walking shoes"
        ),
        "source_url": "https://example.com/lisbon-weather",
    }


@pytest.fixture()
def sample_destination(
    sample_point_of_interest: Dict[str, Any],
    sample_event: Dict[str, Any],
    sample_weather_forecast: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a fully-populated Destination dict.

    Contains one POI, one event, and a weather forecast so
    downstream tests can verify nested model parsing.
    """
    return {
        "name": "Lisbon",
        "country": "Portugal",
        "rationale": (
            "Rich history, world-class food scene, "
            "mild June weather"
        ),
        "points_of_interest": [
            deepcopy(sample_point_of_interest),
        ],
        "events": [deepcopy(sample_event)],
        "weather": deepcopy(sample_weather_forecast),
    }


@pytest.fixture()
def sample_itinerary_response(
    sample_destination: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a complete ItineraryResponse dict.

    Includes one destination and a generated_at timestamp.
    """
    return {
        "destinations": [deepcopy(sample_destination)],
        "generated_at": "2026-03-12T10:30:00Z",
    }


# ------------------------------------------------------------------
# Settings fixture
# ------------------------------------------------------------------

@pytest.fixture()
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Inject safe test values for every env var Settings reads.

    Uses ``monkeypatch`` so env changes are automatically
    reverted after the test.  Returns ``None`` — callers
    import ``Settings`` themselves after env is prepared.
    """
    env_vars: Dict[str, str] = {
        "AZURE_OPENAI_ENDPOINT": (
            "https://test.openai.azure.com/"
        ),
        "AZURE_OPENAI_DEPLOYMENT": "gpt-4o",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


# ------------------------------------------------------------------
# Phase 2 fixtures: Agent and search tool mocking
# ------------------------------------------------------------------


@pytest.fixture()
def sample_search_results() -> List[Dict[str, str]]:
    """Return a list of mock Bing search result dicts.

    Each result has: title, url, snippet.
    """
    return [
        {
            "title": "Lisbon Travel Guide",
            "url": "https://example.com/lisbon-guide",
            "snippet": (
                "Discover Lisbon's rich history, world-class "
                "cuisine, and nearby hiking trails."
            ),
        },
        {
            "title": "Porto Food Scene",
            "url": "https://example.com/porto-food",
            "snippet": (
                "Porto offers medieval history and renowned "
                "wine cellars."
            ),
        },
        {
            "title": "Krakow Historic Sites",
            "url": "https://example.com/krakow",
            "snippet": (
                "Explore Krakow's Old Town and taste "
                "traditional Polish cuisine."
            ),
        },
    ]


@pytest.fixture()
def mock_search_web(
    sample_search_results: List[Dict[str, str]]
) -> Any:
    """Return a context manager that mocks search_web tool.

    Use with ``with mock_search_web:`` in tests to patch the
    web search function.
    """
    with patch(
        "src.agents.tools.web_search.search_web"
    ) as mock_search:
        mock_search.return_value = sample_search_results
        yield mock_search
