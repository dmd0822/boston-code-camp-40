"""Pydantic models shared between API routes and agents."""

from src.api.models.customer import CustomerProfile, TravelDates
from src.api.models.itinerary import (
    Destination,
    Event,
    EventDates,
    ItineraryResponse,
    PointOfInterest,
    WeatherForecast,
)

__all__ = [
    "CustomerProfile",
    "Destination",
    "Event",
    "EventDates",
    "ItineraryResponse",
    "PointOfInterest",
    "TravelDates",
    "WeatherForecast",
]
