---
name: "backend-error-contract-testing"
description: "Define and verify typed backend error contracts across FastAPI, orchestrators, agents, and tools"
domain: "testing"
confidence: "high"
source: "earned — Phase 6.1 backend error coverage"
---

## Context

Use this skill when backend work introduces structured error handling
and you need tests that pin down the contract before or during
implementation.

## Patterns

- Test API errors at the HTTP layer with `TestClient` and
  `raise_server_exceptions=False` so assertions inspect the real
  response body.
- Prefer one shared assertion helper for the API error envelope to
  verify `detail`, `error.code`, `error.message`, and
  `error.details` consistently.
- For orchestrators, separate partial-failure tests from total-failure
  tests:
  - one specialist fails -> assert graceful degradation
  - all specialists fail -> assert typed orchestration error
  - timeouts -> assert either typed timeout errors or preserved partial
    results, depending on architecture
- For agent wrappers, patch the agent factory and drive failures via
  the public async function so tests validate exception translation,
  not just helper internals.
- Keep tool tests specific to transport-level conditions (timeouts,
  invalid credentials, rate limits) and assert graceful fallback.

## Examples

- `tests/integration/test_api_routes.py` — structured 422/500/504
  error response coverage.
- `tests/unit/orchestrator/test_travel_orchestrator.py` — graceful
  degradation vs. hard failure coverage.
- `tests/unit/agents/test_agent_error_handling.py` — typed agent error
  translation tests.
- `tests/unit/tools/test_web_search.py` — Bing timeout/401/429 tests.

## Anti-Patterns

- Do not assert raw stack traces or framework default error payloads if
  the backend is moving to a stable contract.
- Do not test only generic `Exception`; use the typed error classes the
  API layer is expected to understand.
- Do not mix partial-failure expectations with total-failure contracts
  in the same test.
