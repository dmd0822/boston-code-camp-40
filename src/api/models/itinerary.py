"""Pydantic models for the itinerary response."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PointOfInterest(BaseModel):
    """A point of interest recommended for a destination.

    Each POI is grounded in web search results and includes
    a source URL for traceability.
    """

    name: str = Field(
        ...,
        description="Name of the attraction or place",
    )
    description: str = Field(
        ...,
        description="Brief description of the POI",
    )
    category: str = Field(
        ...,
        description="Category (e.g. 'history', 'food', 'nature')",
    )
    visit_duration_hours: float = Field(
        ...,
        gt=0,
        description="Estimated visit duration in hours",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="URL of the source used for this POI",
    )


class EventDates(BaseModel):
    """Start and end dates for an event."""

    start: date = Field(
        ...,
        description="Event start date",
    )
    end: date = Field(
        ...,
        description="Event end date",
    )


class Event(BaseModel):
    """A festival, fair, or special event at a destination.

    Events are date-scoped to the travel window. If no
    matching events exist, an empty list is returned — never
    fabricated entries.
    """

    name: str = Field(
        ...,
        description="Name of the event",
    )
    dates: EventDates = Field(
        ...,
        description="Start and end dates of the event",
    )
    description: str = Field(
        ...,
        description="Brief description of the event",
    )
    venue: str = Field(
        ...,
        description="Venue or area where the event takes place",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="URL of the source used for this event",
    )


class WeatherForecast(BaseModel):
    """Historical weather expectations for a destination.

    Based on historical averages, not real-time forecasts.
    All data is grounded in web search results.
    """

    avg_high_celsius: float = Field(
        ...,
        description="Average daily high temperature in Celsius",
    )
    avg_low_celsius: float = Field(
        ...,
        description="Average daily low temperature in Celsius",
    )
    precipitation_chance: str = Field(
        ...,
        description="Precipitation likelihood (e.g. 'low')",
    )
    clothing_suggestion: str = Field(
        ...,
        description="What to pack based on weather",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="URL of the weather data source",
    )


class Destination(BaseModel):
    """A travel destination with enriched detail.

    Produced by the General Agent and enriched by the POI,
    Event, and Weather specialist agents.
    """

    name: str = Field(
        ...,
        description="Destination city or region name",
    )
    country: str = Field(
        ...,
        description="Country of the destination",
    )
    rationale: str = Field(
        ...,
        description="Why this destination matches the profile",
    )
    points_of_interest: List[PointOfInterest] = Field(
        default_factory=list,
        description="Recommended places to visit",
    )
    events: List[Event] = Field(
        default_factory=list,
        description="Events during the travel window",
    )
    weather: Optional[WeatherForecast] = Field(
        default=None,
        description="Expected weather conditions",
    )


class ItineraryResponse(BaseModel):
    """Full itinerary returned to the frontend.

    Contains one or more enriched destinations and a
    generation timestamp for cache-busting / display.
    """

    destinations: List[Destination] = Field(
        ...,
        description="List of recommended destinations",
    )
    generated_at: datetime = Field(
        ...,
        description="UTC timestamp when the itinerary was built",
    )
