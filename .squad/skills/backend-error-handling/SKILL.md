---
name: "backend-error-handling"
description: "Consistent FastAPI, orchestrator, and agent error handling for this travel backend"
domain: "error-handling"
confidence: "high"
source: "earned — implemented during Phase 6.1 hardening"
---

## Context

Use this skill when backend work touches FastAPI routes, Azure OpenAI
agent calls, the Bing Search grounding tool, or the itinerary
orchestrator. The goal is to return safe, consistent JSON errors while
preserving partial itinerary results when only specialist agents fail.

## Patterns

- Define shared backend exceptions in `src/exceptions.py` with stable
  HTTP semantics (`ServiceConfigurationError`,
  `ExternalServiceTimeoutError`, `ExternalServiceError`,
  `ItineraryGenerationError`).
- Register FastAPI-wide handlers in `src/api/error_handlers.py` and
  keep every API failure in the envelope
  `{"error": {"code", "message", "details"}, "detail": "..."}`.
- Put semantic request validation in Pydantic models instead of the
  route body when possible. This project now validates travel date
  order plus trimmed, non-blank interests and departure cities in
  `src/api/models/customer.py`.
- Centralize Azure OpenAI timeout and response parsing logic in
  `src/agents/agent_utils.py` so agent modules stay small and behave
  consistently.
- In the orchestrator, wrap specialist agent calls with a result type
  that records whether the returned default value came from a failure.
  This lets the backend distinguish a legitimate empty result from a
  fallback caused by agent failure.
- Treat Bing Search as optional. `src/agents/tools/web_search.py`
  should log and return `[]` on timeout, HTTP, request, credential, or
  JSON parsing issues instead of crashing the request.

## Examples

- `src/api/error_handlers.py` — shared JSON error envelope and FastAPI
  exception registration.
- `src/api/routes/itinerary.py` — route-level translation of timeout,
  configuration, and unexpected failures.
- `src/orchestrator/travel_orchestrator.py` — partial degradation for
  specialist failures, hard failure when every specialist fails.
- `tests/integration/test_api_routes.py` — assertions for 422/500/504
  structured error responses.

## Anti-Patterns

- Returning different JSON shapes for validation vs runtime errors.
- Silently converting a General Agent failure into a successful empty
  itinerary response.
- Swallowing every specialist failure without recording whether the
  returned empty value came from a real no-data case or a fallback.
- Letting Azure OpenAI or Bing Search timeout exceptions bubble to the
  client as stack traces.
