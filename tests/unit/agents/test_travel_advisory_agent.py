"""Unit tests for the Travel Advisory Agent.

Tests the agent's ability to look up U.S. State Department
travel advisories for destinations. Covers advisory levels
1-4, unknown destinations, null responses, invalid payloads,
and hallucination validation. All tests use mocked LLM
responses — no real Azure OpenAI or Bing Search API calls.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.models.customer import TravelDates
from src.api.models.itinerary import TravelAdvisory
from src.config.settings import Settings
from src.exceptions import ExternalServiceError


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def mock_advisory_responses() -> Dict[str, Any]:
    """Load all mock LLM responses for Travel Advisory Agent."""
    with open(
        "tests/fixtures/agent_responses/"
        "travel_advisory_agent.json",
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


@pytest.fixture()
def mock_level1_response(
    mock_advisory_responses: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a Level 1 (Normal Precautions) advisory."""
    return mock_advisory_responses["advisory_level_1"]


@pytest.fixture()
def mock_level2_response(
    mock_advisory_responses: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a Level 2 (Increased Caution) advisory."""
    return mock_advisory_responses["advisory_level_2"]


@pytest.fixture()
def mock_level3_response(
    mock_advisory_responses: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a Level 3 (Reconsider Travel) advisory."""
    return mock_advisory_responses["advisory_level_3"]


@pytest.fixture()
def mock_level4_response(
    mock_advisory_responses: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a Level 4 (Do Not Travel) advisory."""
    return mock_advisory_responses["advisory_level_4"]


@pytest.fixture()
def travel_dates() -> TravelDates:
    """Return valid travel dates for advisory lookups."""
    return TravelDates(
        start=date(2026, 6, 15),
        end=date(2026, 6, 25),
    )


# ------------------------------------------------------------------
# Helper — patch the agent pipeline
# ------------------------------------------------------------------


def _patch_agent_pipeline(response_text: str):
    """Return nested context managers that mock the full agent.

    Patches DefaultAzureCredential, AzureAIClient, Agent, and
    the system prompt loader so ``get_travel_advisory`` runs
    without any real external calls.

    Args:
        response_text: The text the mock agent.run() returns.

    Returns:
        Nested context manager for use with ``with``.
    """
    mock_response = MagicMock()
    mock_response.text = response_text

    cred_patch = patch(
        "src.agents.travel_advisory_agent."
        "DefaultAzureCredential"
    )
    client_patch = patch(
        "src.agents.travel_advisory_agent.AzureAIClient"
    )
    agent_patch = patch(
        "src.agents.travel_advisory_agent.Agent"
    )
    prompt_patch = patch(
        "src.agents.travel_advisory_agent._load_system_prompt",
        return_value="system prompt",
    )

    class PipelineContext:
        """Context manager that applies all agent patches."""

        def __enter__(self):
            """Enter all patch contexts and wire the mock."""
            self._cred = cred_patch.__enter__()
            self._client = client_patch.__enter__()
            self._agent_cls = agent_patch.__enter__()
            self._prompt = prompt_patch.__enter__()

            mock_instance = MagicMock()
            mock_instance.run = AsyncMock(
                return_value=mock_response
            )
            self._agent_cls.return_value = mock_instance
            return self

        def __exit__(self, *args):
            """Exit all patch contexts."""
            prompt_patch.__exit__(*args)
            agent_patch.__exit__(*args)
            client_patch.__exit__(*args)
            cred_patch.__exit__(*args)

    return PipelineContext()


# ------------------------------------------------------------------
# Tests — Advisory level parsing (Levels 1-4)
# ------------------------------------------------------------------


class TestTravelAdvisoryLevelParsing:
    """Test advisory level parsing across the 1-4 scale."""

    @pytest.mark.asyncio
    async def test_level_1_normal_precautions(
        self,
        mock_settings: None,
        mock_level1_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify Level 1 advisory parsed correctly.

        Level 1 = Exercise Normal Precautions. Should return
        a valid TravelAdvisory with advisory_level == 1.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level1_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Lisbon", "Portugal", travel_dates, settings
            )

        assert isinstance(advisory, TravelAdvisory)
        assert advisory.advisory_level == 1

    @pytest.mark.asyncio
    async def test_level_2_increased_caution(
        self,
        mock_settings: None,
        mock_level2_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify Level 2 advisory parsed correctly.

        Level 2 = Exercise Increased Caution.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level2_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Mexico City",
                "Mexico",
                travel_dates,
                settings,
            )

        assert isinstance(advisory, TravelAdvisory)
        assert advisory.advisory_level == 2

    @pytest.mark.asyncio
    async def test_level_3_reconsider_travel(
        self,
        mock_settings: None,
        mock_level3_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify Level 3 advisory parsed correctly.

        Level 3 = Reconsider Travel.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level3_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Islamabad",
                "Pakistan",
                travel_dates,
                settings,
            )

        assert isinstance(advisory, TravelAdvisory)
        assert advisory.advisory_level == 3

    @pytest.mark.asyncio
    async def test_level_4_do_not_travel(
        self,
        mock_settings: None,
        mock_level4_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify Level 4 advisory parsed correctly.

        Level 4 = Do Not Travel.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level4_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Damascus",
                "Syria",
                travel_dates,
                settings,
            )

        assert isinstance(advisory, TravelAdvisory)
        assert advisory.advisory_level == 4


# ------------------------------------------------------------------
# Tests — Unknown/invalid destination
# ------------------------------------------------------------------


class TestUnknownDestination:
    """Test handling of unknown or invalid destinations."""

    @pytest.mark.asyncio
    async def test_null_response_returns_none(
        self,
        mock_settings: None,
        travel_dates: TravelDates,
    ) -> None:
        """Verify agent returning 'null' yields None.

        When the LLM cannot find an advisory, it returns the
        string 'null'. The agent should return None gracefully.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()

        with _patch_agent_pipeline("null"):
            result = await get_travel_advisory(
                "Fake City XYZ",
                "Unknown",
                travel_dates,
                settings,
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_null_case_insensitive(
        self,
        mock_settings: None,
        travel_dates: TravelDates,
    ) -> None:
        """Verify 'NULL' (uppercase) also returns None.

        The agent normalizes to lowercase before checking.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()

        with _patch_agent_pipeline("NULL"):
            result = await get_travel_advisory(
                "Nowhere",
                "Neverland",
                travel_dates,
                settings,
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_non_dict_payload_raises_error(
        self,
        mock_settings: None,
        travel_dates: TravelDates,
    ) -> None:
        """Verify non-dict JSON payload raises ExternalServiceError.

        If the LLM returns a JSON array instead of an object,
        the agent should raise a structured error.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()

        with _patch_agent_pipeline('["not", "a", "dict"]'):
            with pytest.raises(ExternalServiceError):
                await get_travel_advisory(
                    "Lisbon",
                    "Portugal",
                    travel_dates,
                    settings,
                )

    @pytest.mark.asyncio
    async def test_malformed_json_raises_error(
        self,
        mock_settings: None,
        travel_dates: TravelDates,
    ) -> None:
        """Verify malformed JSON raises ExternalServiceError.

        Broken JSON from the LLM should not crash with an
        unhandled exception.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()

        with _patch_agent_pipeline("{broken json!!!"):
            with pytest.raises(ExternalServiceError):
                await get_travel_advisory(
                    "Lisbon",
                    "Portugal",
                    travel_dates,
                    settings,
                )

    @pytest.mark.asyncio
    async def test_invalid_advisory_data_returns_none(
        self,
        mock_settings: None,
        travel_dates: TravelDates,
    ) -> None:
        """Verify invalid advisory data returns None gracefully.

        If the JSON is a dict but fails Pydantic validation
        (e.g. missing required fields), the agent returns None
        instead of crashing.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        bad_data = json.dumps({"advisory_level": 2})

        with _patch_agent_pipeline(bad_data):
            result = await get_travel_advisory(
                "Lisbon",
                "Portugal",
                travel_dates,
                settings,
            )

        assert result is None


# ------------------------------------------------------------------
# Tests — Specific warnings extraction
# ------------------------------------------------------------------


class TestSpecificWarnings:
    """Test specific_warnings field extraction."""

    @pytest.mark.asyncio
    async def test_warnings_list_populated(
        self,
        mock_settings: None,
        mock_level2_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify specific_warnings is a non-empty list.

        Every advisory should have at least one warning.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level2_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Mexico City",
                "Mexico",
                travel_dates,
                settings,
            )

        assert isinstance(advisory.specific_warnings, list)
        assert len(advisory.specific_warnings) >= 1

    @pytest.mark.asyncio
    async def test_warnings_are_strings(
        self,
        mock_settings: None,
        mock_level4_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify each warning is a non-empty string."""
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level4_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Damascus",
                "Syria",
                travel_dates,
                settings,
            )

        for warning in advisory.specific_warnings:
            assert isinstance(warning, str)
            assert len(warning) > 0

    @pytest.mark.asyncio
    async def test_level_4_has_multiple_warnings(
        self,
        mock_settings: None,
        mock_level4_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify Level 4 (Do Not Travel) has multiple warnings.

        High-risk destinations typically have several specific
        concerns documented.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level4_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Damascus",
                "Syria",
                travel_dates,
                settings,
            )

        assert len(advisory.specific_warnings) > 1


# ------------------------------------------------------------------
# Tests — Source URL population
# ------------------------------------------------------------------


class TestSourceUrl:
    """Test source_url field population."""

    @pytest.mark.asyncio
    async def test_source_url_populated(
        self,
        mock_settings: None,
        mock_level1_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify source_url is always present and non-empty."""
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level1_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Lisbon",
                "Portugal",
                travel_dates,
                settings,
            )

        assert advisory.source_url
        assert len(advisory.source_url) > 10

    @pytest.mark.asyncio
    async def test_source_url_is_valid_url(
        self,
        mock_settings: None,
        mock_level1_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify source_url looks like a real URL."""
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level1_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Lisbon",
                "Portugal",
                travel_dates,
                settings,
            )

        assert advisory.source_url.startswith("http")


# ------------------------------------------------------------------
# Tests — Hallucination validation
# ------------------------------------------------------------------


class TestHallucinationValidation:
    """Validate advisory data against known State Dept patterns.

    These tests catch AI hallucinations by verifying the output
    references authoritative sources and uses the correct
    advisory scale.
    """

    @pytest.mark.asyncio
    async def test_source_references_state_gov(
        self,
        mock_settings: None,
        mock_level1_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify source URL references travel.state.gov.

        The authoritative source for U.S. travel advisories is
        the State Department website. Any other domain is
        likely a hallucination.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level1_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Lisbon",
                "Portugal",
                travel_dates,
                settings,
            )

        assert "travel.state.gov" in advisory.source_url

    @pytest.mark.asyncio
    async def test_advisory_level_within_state_dept_scale(
        self,
        mock_settings: None,
        mock_level2_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify advisory_level is within the 1-4 scale.

        The State Department only uses levels 1 through 4.
        Any value outside this range is a hallucination.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level2_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Mexico City",
                "Mexico",
                travel_dates,
                settings,
            )

        assert 1 <= advisory.advisory_level <= 4

    @pytest.mark.asyncio
    async def test_advisory_summary_not_empty(
        self,
        mock_settings: None,
        mock_level3_response: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify advisory_summary is substantive, not empty.

        A blank summary would indicate the LLM failed to
        extract real advisory information.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()
        response_json = json.dumps(mock_level3_response)

        with _patch_agent_pipeline(response_json):
            advisory = await get_travel_advisory(
                "Islamabad",
                "Pakistan",
                travel_dates,
                settings,
            )

        assert advisory.advisory_summary
        assert len(advisory.advisory_summary) > 10

    @pytest.mark.asyncio
    async def test_all_levels_reference_state_gov(
        self,
        mock_settings: None,
        mock_advisory_responses: Dict[str, Any],
        travel_dates: TravelDates,
    ) -> None:
        """Verify all advisory levels reference travel.state.gov.

        Parametric check across all four advisory level
        fixtures to ensure grounding is consistent.
        """
        pytest.importorskip(
            "src.agents.travel_advisory_agent"
        )
        from src.agents.travel_advisory_agent import (
            get_travel_advisory,
        )

        settings = Settings()

        test_cases = [
            (
                "advisory_level_1",
                "Lisbon",
                "Portugal",
            ),
            (
                "advisory_level_2",
                "Mexico City",
                "Mexico",
            ),
            (
                "advisory_level_3",
                "Islamabad",
                "Pakistan",
            ),
            (
                "advisory_level_4",
                "Damascus",
                "Syria",
            ),
        ]

        for key, city, country in test_cases:
            response_data = mock_advisory_responses[key]
            response_json = json.dumps(response_data)

            with _patch_agent_pipeline(response_json):
                advisory = await get_travel_advisory(
                    city,
                    country,
                    travel_dates,
                    settings,
                )

            assert advisory is not None, (
                f"Advisory for {city}, {country} was None"
            )
            assert "travel.state.gov" in advisory.source_url, (
                f"Advisory for {city} does not reference "
                f"travel.state.gov: {advisory.source_url}"
            )
