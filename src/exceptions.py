"""Shared exception types for backend error handling.

These exceptions carry HTTP status metadata so the API layer can
return consistent JSON error responses without duplicating mapping
logic in each route.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ApplicationError(Exception):
    """Base class for expected backend failures.

    Attributes:
        status_code: HTTP status code to return from the API.
        error_code: Stable machine-readable error code.
        details: Optional structured details for debugging.
    """

    status_code: int = 500
    error_code: str = "application_error"

    def __init__(
        self,
        message: str,
        *,
        details: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize the application error.

        Args:
            message: Human-readable description of the failure.
            details: Optional structured details for the response.
        """
        super().__init__(message)
        self.message = message
        self.details = details or []


class InputValidationError(ApplicationError):
    """Raised when request payload validation fails."""

    status_code = 422
    error_code = "validation_error"


class ServiceConfigurationError(ApplicationError):
    """Raised when the backend is missing required configuration."""

    status_code = 503
    error_code = "service_configuration_error"


class ExternalServiceTimeoutError(ApplicationError):
    """Raised when an upstream service call times out."""

    status_code = 504
    error_code = "external_service_timeout"


class ExternalServiceError(ApplicationError):
    """Raised when an upstream dependency fails unexpectedly."""

    status_code = 502
    error_code = "external_service_error"


class ItineraryGenerationError(ApplicationError):
    """Raised when itinerary generation cannot complete."""

    status_code = 500
    error_code = "itinerary_generation_error"
