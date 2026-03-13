"""Integration tests for the API routes.

Tests the FastAPI routes with TestClient to verify:
1. Health endpoint returns healthy status
2. Itinerary endpoint accepts valid input and returns 200
3. Itinerary endpoint rejects invalid input with 422
4. Orchestrator errors are handled gracefully

Orchestrator is mocked to avoid real agent execution.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.models.itinerary import (
    Destination,
    ItineraryResponse,
    PointOfInterest,
    WeatherForecast,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def client() -> TestClient:
    """Return a TestClient for the FastAPI app."""
    app = create_app()
    return TestClient(app)


@pytest.fixture()
def error_client() -> TestClient:
    """Return a TestClient that captures server errors as responses."""
    app = create_app()
    return TestClient(app, raise_server_exceptions=False)


def _assert_error_response(
    response: Any,
    expected_status: int,
    expected_code: str,
) -> Dict[str, Any]:
    """Assert the response uses the standard API error envelope."""
    assert response.status_code == expected_status
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("application/json")

    data = response.json()
    assert isinstance(data["detail"], str)
    assert data["detail"]
    assert data["detail"] == data["error"]["message"]
    assert data["error"]["code"] == expected_code
    assert isinstance(data["error"]["details"], list)
    assert "Traceback" not in json.dumps(data)
    return data


@pytest.fixture()
def mock_itinerary() -> ItineraryResponse:
    """Return a mock ItineraryResponse for orchestrator mocking."""
    destination = Destination(
        name="Lisbon",
        country="Portugal",
        rationale=(
            "Rich history, world-class food scene, "
            "mild June weather"
        ),
        points_of_interest=[
            PointOfInterest(
                name="Belém Tower",
                description=(
                    "UNESCO World Heritage Site and iconic "
                    "Lisbon landmark."
                ),
                category="history",
                visit_duration_hours=1.5,
                source_url="https://example.com/belem-tower",
            ),
        ],
        events=[],
        weather=WeatherForecast(
            avg_high_celsius=27.0,
            avg_low_celsius=17.0,
            precipitation_chance="low",
            clothing_suggestion=(
                "Light layers, comfortable walking shoes"
            ),
            source_url="https://example.com/lisbon-weather",
        ),
    )
    return ItineraryResponse(
        destinations=[destination],
        generated_at=datetime.now(timezone.utc),
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestHealthEndpoint:
    """Test suite for the health check endpoint."""

    def test_health_endpoint_returns_200(
        self, client: TestClient
    ) -> None:
        """Verify GET /api/health returns 200 with healthy status.

        Health endpoint is used by infrastructure probes to
        verify service is responsive.
        """
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestItineraryEndpoint:
    """Test suite for the itinerary generation endpoint."""

    def test_post_itinerary_returns_200_with_valid_input(
        self,
        client: TestClient,
        sample_customer_profile: Dict[str, Any],
        mock_itinerary: ItineraryResponse,
    ) -> None:
        """Verify POST /api/itinerary returns 200 with valid input.

        Full happy path with mocked orchestrator to avoid real
        agent execution.
        """
        with patch(
            "src.api.routes.itinerary.TravelOrchestrator"
        ) as MockOrch:
            mock_instance = MagicMock()
            mock_instance.generate_itinerary = AsyncMock(
                return_value=mock_itinerary
            )
            MockOrch.return_value = mock_instance

            response = client.post(
                "/api/itinerary", json=sample_customer_profile
            )

            assert response.status_code == 200
            data = response.json()
            assert "destinations" in data
            assert "generated_at" in data
            assert isinstance(data["destinations"], list)

    def test_post_itinerary_returns_422_on_invalid_input(
        self, client: TestClient
    ) -> None:
        """Verify invalid customer input returns structured 422 JSON."""
        invalid_profile = {
            "interests": ["history"],
            # Missing budget, travel_dates, party_size,
            # departure_city
        }

        response = client.post(
            "/api/itinerary", json=invalid_profile
        )

        data = _assert_error_response(
            response,
            422,
            "validation_error",
        )
        assert data["error"]["details"]
        first_error = data["error"]["details"][0]
        assert {"field", "message", "type"}.issubset(first_error)

    def test_post_itinerary_rejects_inverted_date_ranges(
        self, client: TestClient
    ) -> None:
        """Verify end dates earlier than start dates are rejected."""
        invalid_profile = {
            "interests": ["history"],
            "budget": "moderate",
            "travel_dates": {
                "start": "2026-06-25",
                "end": "2026-06-15",
            },
            "party_size": 2,
            "departure_city": "Boston",
        }

        response = client.post(
            "/api/itinerary", json=invalid_profile
        )

        data = _assert_error_response(
            response,
            422,
            "validation_error",
        )
        detail_messages = [
            item["message"] for item in data["error"]["details"]
        ]
        assert any("on or after" in message for message in detail_messages)

    def test_post_itinerary_returns_structured_500_on_backend_error(
        self,
        error_client: TestClient,
        sample_customer_profile: Dict[str, Any],
    ) -> None:
        """Verify backend failures return safe 500 JSON, not traces."""
        with patch(
            "src.api.routes.itinerary.TravelOrchestrator"
        ) as MockOrch:
            mock_instance = MagicMock()
            mock_instance.generate_itinerary = AsyncMock(
                side_effect=RuntimeError("database connection lost")
            )
            MockOrch.return_value = mock_instance

            response = error_client.post(
                "/api/itinerary", json=sample_customer_profile
            )

        data = _assert_error_response(
            response,
            500,
            "itinerary_generation_error",
        )
        assert "database connection lost" not in json.dumps(data)

    def test_post_itinerary_returns_timeout_error_response(
        self,
        error_client: TestClient,
        sample_customer_profile: Dict[str, Any],
    ) -> None:
        """Verify backend timeouts return structured timeout details."""
        from src.exceptions import ExternalServiceTimeoutError

        with patch(
            "src.api.routes.itinerary.TravelOrchestrator"
        ) as MockOrch:
            mock_instance = MagicMock()
            mock_instance.generate_itinerary = AsyncMock(
                side_effect=ExternalServiceTimeoutError(
                    "The itinerary request timed out."
                )
            )
            MockOrch.return_value = mock_instance

            response = error_client.post(
                "/api/itinerary", json=sample_customer_profile
            )

        data = _assert_error_response(
            response,
            504,
            "external_service_timeout",
        )
        assert "timed out" in data["detail"].lower()

    def test_post_itinerary_response_structure(
        self,
        client: TestClient,
        sample_customer_profile: Dict[str, Any],
        mock_itinerary: ItineraryResponse,
    ) -> None:
        """Verify response has correct structure.

        Response must have destinations array and generated_at
        timestamp.
        """
        with patch(
            "src.api.routes.itinerary.TravelOrchestrator"
        ) as MockOrch:
            mock_instance = MagicMock()
            mock_instance.generate_itinerary = AsyncMock(
                return_value=mock_itinerary
            )
            MockOrch.return_value = mock_instance

            response = client.post(
                "/api/itinerary", json=sample_customer_profile
            )

            assert response.status_code == 200
            data = response.json()
            # Validate structure
            assert "destinations" in data
            assert "generated_at" in data
            assert isinstance(data["destinations"], list)
            assert len(data["destinations"]) > 0
            # Validate destination structure
            dest = data["destinations"][0]
            assert "name" in dest
            assert "country" in dest
            assert "rationale" in dest
            assert "points_of_interest" in dest
            assert "events" in dest
            assert "weather" in dest

    def test_post_itinerary_accepts_valid_budget_values(
        self, client: TestClient, mock_itinerary: ItineraryResponse
    ) -> None:
        """Verify budget field accepts valid enum values.

        Budget must be one of: budget, moderate, luxury.
        """
        valid_profile = {
            "interests": ["history"],
            "budget": "moderate",
            "travel_dates": {
                "start": "2026-06-15",
                "end": "2026-06-25",
            },
            "party_size": 2,
            "departure_city": "Boston",
        }

        with patch(
            "src.api.routes.itinerary.TravelOrchestrator"
        ) as MockOrch:
            mock_instance = MagicMock()
            mock_instance.generate_itinerary = AsyncMock(
                return_value=mock_itinerary
            )
            MockOrch.return_value = mock_instance

            response = client.post(
                "/api/itinerary", json=valid_profile
            )

            assert response.status_code == 200

    def test_post_itinerary_rejects_invalid_budget_value(
        self, client: TestClient
    ) -> None:
        """Verify invalid budget value triggers validation error.

        Budget field has pattern validation for allowed values.
        """
        invalid_profile = {
            "interests": ["history"],
            "budget": "cheap",  # Invalid value
            "travel_dates": {
                "start": "2026-06-15",
                "end": "2026-06-25",
            },
            "party_size": 2,
            "departure_city": "Boston",
        }

        response = client.post(
            "/api/itinerary", json=invalid_profile
        )

        assert response.status_code == 422

    def test_post_itinerary_requires_non_empty_interests(
        self, client: TestClient
    ) -> None:
        """Verify interests field requires at least one item.

        CustomerProfile enforces min_length=1 on interests.
        """
        invalid_profile = {
            "interests": [],  # Empty list
            "budget": "moderate",
            "travel_dates": {
                "start": "2026-06-15",
                "end": "2026-06-25",
            },
            "party_size": 2,
            "departure_city": "Boston",
        }

        response = client.post(
            "/api/itinerary", json=invalid_profile
        )

        assert response.status_code == 422

    def test_post_itinerary_requires_positive_party_size(
        self, client: TestClient
    ) -> None:
        """Verify party_size must be at least 1.

        CustomerProfile enforces ge=1 on party_size.
        """
        invalid_profile = {
            "interests": ["history"],
            "budget": "moderate",
            "travel_dates": {
                "start": "2026-06-15",
                "end": "2026-06-25",
            },
            "party_size": 0,  # Invalid
            "departure_city": "Boston",
        }

        response = client.post(
            "/api/itinerary", json=invalid_profile
        )

        assert response.status_code == 422
