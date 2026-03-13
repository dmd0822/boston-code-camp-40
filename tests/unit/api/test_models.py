"""Comprehensive Pydantic model validation tests.

Tests cover every model in ``src/api/models/`` — positive cases,
required-field enforcement, edge cases, and type coercion.

NOTE: ``source_url`` is Optional in the current models.  The
architecture mandates grounding, but enforcement is at the agent
prompt level, not the schema level.  A decision has been filed.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from typing import Any, Dict, List

import pytest
from pydantic import ValidationError

from src.api.models.customer import CustomerProfile, TravelDates
from src.api.models.itinerary import (
    Destination,
    Event,
    EventDates,
    ItineraryResponse,
    PointOfInterest,
    WeatherForecast,
)


# ==================================================================
# TravelDates
# ==================================================================

class TestTravelDates:
    """Validate TravelDates parsing and constraints."""

    def test_valid_travel_dates(
        self, sample_travel_dates: Dict[str, str]
    ) -> None:
        """Accept well-formed start/end date strings."""
        td = TravelDates(**sample_travel_dates)
        assert td.start == date(2026, 6, 15)
        assert td.end == date(2026, 6, 25)

    @pytest.mark.parametrize(
        "field", ["start", "end"],
    )
    def test_missing_date_field_raises(
        self,
        sample_travel_dates: Dict[str, str],
        field: str,
    ) -> None:
        """Each date field is required."""
        data = deepcopy(sample_travel_dates)
        del data[field]
        with pytest.raises(ValidationError):
            TravelDates(**data)

    @pytest.mark.parametrize(
        "bad_date",
        [
            "not-a-date",
            "2026/06/15",
            "06-15-2026",
            "",
            "2026-13-01",
        ],
        ids=[
            "plain_text",
            "wrong_separator",
            "us_format",
            "empty_string",
            "month_13",
        ],
    )
    def test_invalid_date_format_raises(
        self, bad_date: str
    ) -> None:
        """Reject clearly-invalid date formats."""
        with pytest.raises(ValidationError):
            TravelDates(start=bad_date, end="2026-06-25")

    def test_same_start_and_end_is_accepted(self) -> None:
        """A one-day trip (start == end) should not error."""
        td = TravelDates(start="2026-06-15", end="2026-06-15")
        assert td.start == td.end

    def test_end_before_start_is_rejected(self) -> None:
        """Trips cannot end before they begin."""
        with pytest.raises(ValidationError):
            TravelDates(start="2026-06-25", end="2026-06-15")


# ==================================================================
# CustomerProfile
# ==================================================================

class TestCustomerProfile:
    """Validate CustomerProfile creation and field rules."""

    def test_valid_profile(
        self, sample_customer_profile: Dict[str, Any]
    ) -> None:
        """A fully-populated profile parses without error."""
        cp = CustomerProfile(**sample_customer_profile)
        assert cp.departure_city == "Boston"
        assert cp.party_size == 2
        assert len(cp.interests) == 3

    @pytest.mark.parametrize(
        "field",
        [
            "interests",
            "budget",
            "travel_dates",
            "party_size",
            "departure_city",
        ],
    )
    def test_missing_required_field_raises(
        self,
        sample_customer_profile: Dict[str, Any],
        field: str,
    ) -> None:
        """Every required field must be present."""
        data = deepcopy(sample_customer_profile)
        del data[field]
        with pytest.raises(ValidationError):
            CustomerProfile(**data)

    def test_empty_interests_list_rejected(
        self, sample_customer_profile: Dict[str, Any]
    ) -> None:
        """An empty interests list is rejected (min_length=1).

        At least one interest is required so agents can scope
        their search queries meaningfully.
        """
        data = deepcopy(sample_customer_profile)
        data["interests"] = []
        with pytest.raises(ValidationError):
            CustomerProfile(**data)

    @pytest.mark.parametrize(
        "bad_budget",
        ["cheap", "expensive", "MODERATE", "", "123"],
        ids=[
            "not_enum_cheap",
            "not_enum_expensive",
            "wrong_case",
            "empty",
            "numeric_string",
        ],
    )
    def test_budget_rejects_invalid_tier(
        self,
        sample_customer_profile: Dict[str, Any],
        bad_budget: str,
    ) -> None:
        """``budget`` must be one of: budget, moderate, luxury."""
        data = deepcopy(sample_customer_profile)
        data["budget"] = bad_budget
        with pytest.raises(ValidationError):
            CustomerProfile(**data)

    @pytest.mark.parametrize(
        "valid_budget", ["budget", "moderate", "luxury"],
    )
    def test_budget_accepts_valid_tiers(
        self,
        sample_customer_profile: Dict[str, Any],
        valid_budget: str,
    ) -> None:
        """All three budget tiers are accepted."""
        data = deepcopy(sample_customer_profile)
        data["budget"] = valid_budget
        cp = CustomerProfile(**data)
        assert cp.budget == valid_budget

    def test_notes_optional_none(
        self, sample_customer_profile: Dict[str, Any]
    ) -> None:
        """``notes`` is optional; None must be accepted."""
        data = deepcopy(sample_customer_profile)
        data["notes"] = None
        cp = CustomerProfile(**data)
        assert cp.notes is None

    def test_notes_optional_absent(
        self, sample_customer_profile: Dict[str, Any]
    ) -> None:
        """``notes`` may be omitted entirely."""
        data = deepcopy(sample_customer_profile)
        data.pop("notes", None)
        cp = CustomerProfile(**data)
        assert cp.notes is None

    @pytest.mark.parametrize(
        "bad_size",
        [0, -1, -100],
        ids=["zero", "negative_one", "large_negative"],
    )
    def test_party_size_must_be_positive(
        self,
        sample_customer_profile: Dict[str, Any],
        bad_size: int,
    ) -> None:
        """``party_size`` must be a positive integer (>= 1)."""
        data = deepcopy(sample_customer_profile)
        data["party_size"] = bad_size
        with pytest.raises(ValidationError):
            CustomerProfile(**data)

    def test_party_size_rejects_non_integer(
        self, sample_customer_profile: Dict[str, Any]
    ) -> None:
        """``party_size`` must be an integer, not a string."""
        data = deepcopy(sample_customer_profile)
        data["party_size"] = "two"
        with pytest.raises(ValidationError):
            CustomerProfile(**data)

    def test_invalid_travel_dates_propagates(
        self, sample_customer_profile: Dict[str, Any]
    ) -> None:
        """Bad nested TravelDates should raise on the parent."""
        data = deepcopy(sample_customer_profile)
        data["travel_dates"] = {"start": "bad", "end": "bad"}
        with pytest.raises(ValidationError):
            CustomerProfile(**data)


# ==================================================================
# PointOfInterest
# ==================================================================

class TestPointOfInterest:
    """Validate PointOfInterest fields and grounding rule."""

    def test_valid_poi(
        self, sample_point_of_interest: Dict[str, Any]
    ) -> None:
        """A fully-populated POI parses without error."""
        poi = PointOfInterest(**sample_point_of_interest)
        assert poi.name == "Belém Tower"
        assert poi.visit_duration_hours == 1.5

    def test_source_url_optional(
        self, sample_point_of_interest: Dict[str, Any]
    ) -> None:
        """``source_url`` is optional at the schema level.

        Grounding enforcement happens at the agent prompt layer.
        The model allows None so partial / in-progress results
        can be represented.
        """
        data = deepcopy(sample_point_of_interest)
        del data["source_url"]
        poi = PointOfInterest(**data)
        assert poi.source_url is None

    @pytest.mark.parametrize(
        "field",
        ["name", "description", "category"],
    )
    def test_missing_text_field_raises(
        self,
        sample_point_of_interest: Dict[str, Any],
        field: str,
    ) -> None:
        """Core text fields are required."""
        data = deepcopy(sample_point_of_interest)
        del data[field]
        with pytest.raises(ValidationError):
            PointOfInterest(**data)

    @pytest.mark.parametrize(
        "bad_duration",
        [0, -1, -0.5],
        ids=["zero", "neg_int", "neg_float"],
    )
    def test_visit_duration_must_be_positive(
        self,
        sample_point_of_interest: Dict[str, Any],
        bad_duration: float,
    ) -> None:
        """``visit_duration_hours`` must be > 0."""
        data = deepcopy(sample_point_of_interest)
        data["visit_duration_hours"] = bad_duration
        with pytest.raises(ValidationError):
            PointOfInterest(**data)


# ==================================================================
# Event
# ==================================================================

class TestEvent:
    """Validate Event model fields and grounding rule."""

    def test_valid_event(
        self, sample_event: Dict[str, Any]
    ) -> None:
        """A fully-populated event parses without error."""
        ev = Event(**sample_event)
        assert ev.name == "Festa de Santo António"
        assert ev.venue == "Alfama district"

    def test_source_url_optional(
        self, sample_event: Dict[str, Any]
    ) -> None:
        """``source_url`` is optional at the schema level."""
        data = deepcopy(sample_event)
        del data["source_url"]
        ev = Event(**data)
        assert ev.source_url is None

    def test_missing_name_raises(
        self, sample_event: Dict[str, Any]
    ) -> None:
        """``name`` is required — cannot create unnamed event."""
        data = deepcopy(sample_event)
        del data["name"]
        with pytest.raises(ValidationError):
            Event(**data)

    @pytest.mark.parametrize(
        "field",
        ["description", "venue", "dates"],
    )
    def test_missing_required_fields(
        self,
        sample_event: Dict[str, Any],
        field: str,
    ) -> None:
        """All core event fields are required."""
        data = deepcopy(sample_event)
        del data[field]
        with pytest.raises(ValidationError):
            Event(**data)

    def test_invalid_event_dates_raises(
        self, sample_event: Dict[str, Any]
    ) -> None:
        """Malformed dates nested inside Event must fail."""
        data = deepcopy(sample_event)
        data["dates"] = {"start": "nope", "end": "nope"}
        with pytest.raises(ValidationError):
            Event(**data)


# ==================================================================
# WeatherForecast
# ==================================================================

class TestWeatherForecast:
    """Validate WeatherForecast fields and grounding rule."""

    def test_valid_forecast(
        self, sample_weather_forecast: Dict[str, Any]
    ) -> None:
        """A complete forecast parses without error."""
        wf = WeatherForecast(**sample_weather_forecast)
        assert wf.avg_high_celsius == 27
        assert wf.avg_low_celsius == 17

    def test_source_url_optional(
        self, sample_weather_forecast: Dict[str, Any]
    ) -> None:
        """``source_url`` is optional at the schema level."""
        data = deepcopy(sample_weather_forecast)
        del data["source_url"]
        wf = WeatherForecast(**data)
        assert wf.source_url is None

    @pytest.mark.parametrize(
        "field",
        [
            "avg_high_celsius",
            "avg_low_celsius",
            "precipitation_chance",
            "clothing_suggestion",
        ],
    )
    def test_missing_required_field_raises(
        self,
        sample_weather_forecast: Dict[str, Any],
        field: str,
    ) -> None:
        """Every weather field is required."""
        data = deepcopy(sample_weather_forecast)
        del data[field]
        with pytest.raises(ValidationError):
            WeatherForecast(**data)

    def test_temperature_accepts_numeric_types(
        self,
        sample_weather_forecast: Dict[str, Any],
    ) -> None:
        """Temperatures may be int or float."""
        data = deepcopy(sample_weather_forecast)
        data["avg_high_celsius"] = 27.5
        data["avg_low_celsius"] = 16.8
        wf = WeatherForecast(**data)
        assert wf.avg_high_celsius == 27.5

    def test_temperature_rejects_non_numeric(
        self,
        sample_weather_forecast: Dict[str, Any],
    ) -> None:
        """Temperature values must be numbers, not strings."""
        data = deepcopy(sample_weather_forecast)
        data["avg_high_celsius"] = "warm"
        with pytest.raises(ValidationError):
            WeatherForecast(**data)


# ==================================================================
# Destination
# ==================================================================

class TestDestination:
    """Validate Destination model and nested sub-models."""

    def test_valid_destination(
        self, sample_destination: Dict[str, Any]
    ) -> None:
        """A fully-populated destination parses correctly."""
        dest = Destination(**sample_destination)
        assert dest.name == "Lisbon"
        assert dest.country == "Portugal"
        assert len(dest.points_of_interest) == 1
        assert len(dest.events) == 1
        assert dest.weather is not None

    @pytest.mark.parametrize(
        "field", ["name", "country"],
    )
    def test_missing_identity_field_raises(
        self,
        sample_destination: Dict[str, Any],
        field: str,
    ) -> None:
        """``name`` and ``country`` are required."""
        data = deepcopy(sample_destination)
        del data[field]
        with pytest.raises(ValidationError):
            Destination(**data)

    def test_empty_pois_accepted(
        self, sample_destination: Dict[str, Any]
    ) -> None:
        """Empty POI list is valid — partial results allowed."""
        data = deepcopy(sample_destination)
        data["points_of_interest"] = []
        dest = Destination(**data)
        assert dest.points_of_interest == []

    def test_empty_events_accepted(
        self, sample_destination: Dict[str, Any]
    ) -> None:
        """Empty events list is valid — no events found."""
        data = deepcopy(sample_destination)
        data["events"] = []
        dest = Destination(**data)
        assert dest.events == []

    def test_weather_none_accepted(
        self, sample_destination: Dict[str, Any]
    ) -> None:
        """``weather`` may be None for partial results."""
        data = deepcopy(sample_destination)
        data["weather"] = None
        dest = Destination(**data)
        assert dest.weather is None

    def test_nested_poi_validation_propagates(
        self, sample_destination: Dict[str, Any]
    ) -> None:
        """Invalid nested POI data should surface as error."""
        data = deepcopy(sample_destination)
        # POI missing required source_url
        data["points_of_interest"] = [{"name": "X"}]
        with pytest.raises(ValidationError):
            Destination(**data)


# ==================================================================
# ItineraryResponse
# ==================================================================

class TestItineraryResponse:
    """Validate the top-level itinerary response envelope."""

    def test_valid_response(
        self,
        sample_itinerary_response: Dict[str, Any],
    ) -> None:
        """A complete response with destinations parses OK."""
        resp = ItineraryResponse(**sample_itinerary_response)
        assert len(resp.destinations) == 1
        assert resp.destinations[0].name == "Lisbon"

    def test_empty_destinations_accepted(
        self,
        sample_itinerary_response: Dict[str, Any],
    ) -> None:
        """Empty destinations list is valid.

        Edge case: no matching destinations found for the
        customer profile.  The API should still return 200.
        """
        data = deepcopy(sample_itinerary_response)
        data["destinations"] = []
        resp = ItineraryResponse(**data)
        assert resp.destinations == []

    def test_generated_at_parsed(
        self,
        sample_itinerary_response: Dict[str, Any],
    ) -> None:
        """``generated_at`` is correctly parsed as datetime."""
        resp = ItineraryResponse(**sample_itinerary_response)
        assert isinstance(resp.generated_at, datetime)

    def test_generated_at_required(self) -> None:
        """``generated_at`` is a required field.

        The orchestrator must set the timestamp explicitly
        when building the response.
        """
        data: Dict[str, Any] = {"destinations": []}
        with pytest.raises(ValidationError):
            ItineraryResponse(**data)

    def test_multiple_destinations(
        self,
        sample_destination: Dict[str, Any],
    ) -> None:
        """Response may contain multiple destinations."""
        dest2 = deepcopy(sample_destination)
        dest2["name"] = "Porto"
        data: Dict[str, Any] = {
            "destinations": [
                deepcopy(sample_destination),
                dest2,
            ],
            "generated_at": "2026-03-12T10:30:00Z",
        }
        resp = ItineraryResponse(**data)
        assert len(resp.destinations) == 2
        names = [d.name for d in resp.destinations]
        assert "Lisbon" in names
        assert "Porto" in names

    def test_invalid_destination_in_list_raises(
        self,
    ) -> None:
        """A malformed destination inside the list must fail."""
        # Missing required 'country' and 'rationale'
        data: Dict[str, Any] = {
            "destinations": [{"name": "Nowhere"}],
            "generated_at": "2026-03-12T10:30:00Z",
        }
        with pytest.raises(ValidationError):
            ItineraryResponse(**data)
