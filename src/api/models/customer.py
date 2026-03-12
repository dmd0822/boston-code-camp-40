"""Pydantic models for customer profile input."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class TravelDates(BaseModel):
    """Date range for the trip."""

    start: date = Field(
        ...,
        description="Trip start date",
    )
    end: date = Field(
        ...,
        description="Trip end date",
    )


class CustomerProfile(BaseModel):
    """Customer profile submitted to build an itinerary.

    Contains the traveler's preferences, constraints, and
    logistical details that the agent pipeline uses to select
    destinations and activities.
    """

    interests: List[str] = Field(
        ...,
        min_length=1,
        description="Travel interests (e.g. 'history', 'food')",
    )
    budget: str = Field(
        ...,
        pattern=r"^(budget|moderate|luxury)$",
        description="Budget tier: budget, moderate, or luxury",
    )
    travel_dates: TravelDates = Field(
        ...,
        description="Start and end dates for the trip",
    )
    party_size: int = Field(
        ...,
        ge=1,
        description="Number of travelers",
    )
    departure_city: str = Field(
        ...,
        min_length=1,
        description="City the traveler is departing from",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Free-text notes or preferences",
    )
