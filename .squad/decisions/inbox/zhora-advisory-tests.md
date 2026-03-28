# Decision: Travel Advisory Agent Test Contracts

**Author:** Zhora (Tester)
**Date:** 2026-03-13
**Issue:** #4

## Decision

Tests for the Travel Advisory Agent follow the same patterns as Weather Agent tests:
- `_patch_agent_pipeline()` helper encapsulates all Azure mocking
- `pytest.importorskip()` used for graceful skipping if module doesn't exist
- Mock fixtures in `tests/fixtures/agent_responses/travel_advisory_agent.json`
- Hallucination tests validate `travel.state.gov` grounding

## Impact

- **Batty:** Implementation must return `TravelAdvisory` model with `advisory_level` (1-4), `advisory_summary`, `specific_warnings` (non-empty list), and `source_url` (containing `travel.state.gov`). Return `"null"` string for unknown destinations.
- **Orchestrator:** `get_travel_advisory` is now part of Phase 2 fan-out alongside POI/Event/Weather. Tests verify it's called once per destination and degrades gracefully on failure.
- **Model:** `TravelAdvisory.advisory_level` uses `ge=1, le=4`; `specific_warnings` uses `min_length=1`; `last_updated` is optional.
