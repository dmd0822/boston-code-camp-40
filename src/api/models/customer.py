"""Pydantic models for customer profile input."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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

    @model_validator(mode="after")
    def validate_date_order(self) -> "TravelDates":
        """Ensure the trip end date is not before the start date."""
        if self.end < self.start:
            raise ValueError(
                "travel_dates.end must be on or after "
                "travel_dates.start."
            )
        return self


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

    @field_validator("interests", mode="before")
    @classmethod
    def validate_interests(cls, value: object) -> object:
        """Strip interests and reject blank interest entries."""
        if not isinstance(value, list):
            return value

        cleaned_interests: List[str] = []
        for interest in value:
            if not isinstance(interest, str):
                raise TypeError("Each interest must be a string.")

            normalized_interest = interest.strip()
            if not normalized_interest:
                raise ValueError(
                    "Interests cannot contain blank values."
                )
            cleaned_interests.append(normalized_interest)

        return cleaned_interests

    @field_validator("departure_city")
    @classmethod
    def validate_departure_city(cls, value: str) -> str:
        """Strip the departure city and reject blank values."""
        normalized_city = value.strip()
        if not normalized_city:
            raise ValueError("departure_city cannot be blank.")
        return normalized_city

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: Optional[str]) -> Optional[str]:
        """Trim notes and collapse empty strings to None."""
        if value is None:
            return None

        normalized_notes = value.strip()
        return normalized_notes or None
