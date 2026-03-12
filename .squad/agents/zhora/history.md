# Project Context

- **Owner:** Dave Davis
- **Project:** Travel Agent Application — takes customer information, builds personalized itineraries using multiple AI agents
- **Stack:** Python backend (Microsoft Agent Framework), React frontend, Azure Bicep infrastructure
- **Key Agents:** General (destination matching), POI (points of interest), Event (festivals/fairs), Weather (historical forecasts)
- **Grounding:** All agents grounded in web search to reduce hallucination
- **Scope:** MVP — no auth, no persistence of itineraries
- **Created:** 2026-03-12

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-03-12 — Architecture Design Finalized (Deckard Lead)

**Status:** Approved and ready for implementation sprint

**Key Technical Decisions:**
- **Backend:** FastAPI + Microsoft Agent Framework (customer requirement)
- **Orchestration:** Two-phase deterministic Python (General Agent sequential → POI/Event/Weather concurrent)
- **Grounding:** Mandatory Bing Web Search for all agents (search-first pattern)
- **LLM:** Azure OpenAI (GPT-4o)
- **Frontend:** React + Vite + TypeScript
- **Infrastructure:** Azure Container Apps + Bicep IaC

**Agent Responsibilities:**
- **Weather Agent:** Historical weather data and climate insights
- **Grounding:** Uses shared `src/agents/tools/web_search.py` tool (mandatory search-first)

**Reference Document:** `docs/architecture.md` (37KB, comprehensive MVP architecture)

**What This Means for Zhora:**
- Weather Agent is a dedicated service within the agent framework
- Fan-out execution in concurrent phase with POI/Event agents
- Must implement search-grounded reasoning for weather analysis
- Inputs: destination, travel dates; Output: weather patterns, climate insights, packing recommendations
- No authentication or persistence in MVP scope

### 2026-03-12 — Phase 1 Test Suite Complete (Zhora)

**Status:** 67 tests passing — full Pydantic model coverage

**Key Files:**
- `tests/conftest.py` — shared fixtures (customer, destination, POI, event, weather, itinerary, settings)
- `tests/unit/api/test_models.py` — comprehensive model tests
- `tests/fixtures/agent_responses/.gitkeep` — placeholder for canned LLM responses
- `tests/fixtures/search_results/.gitkeep` — placeholder for mock Bing results

**Discrepancies Found vs Architecture:**
- `source_url` is `Optional` on POI, Event, WeatherForecast — architecture says grounding is mandatory. Decision filed.
- `interests` enforces `min_length=1` — architecture didn't specify; good constraint.
- `budget` uses regex enum (`budget|moderate|luxury`) — architecture didn't specify; good constraint.
- `generated_at` is required (no default) — architecture implied auto-population.
- Batty created `EventDates` as a separate model from `TravelDates` — same structure, different class.

**Testing Patterns:**
- Use `deepcopy()` on fixture dicts before mutation to avoid cross-test contamination
- `pytest.mark.parametrize` for systematic negative testing of each field
- Arrange-Act-Assert via class-per-model organization
- Every test has a docstring explaining what it validates

### 2026-03-12 — Team Phase 1 Status (All Agents)

**Phase 1 Foundation Sprint Complete** — Backend & Tests ready. Scribe finalized all logs and decisions.

**Status by agent:**
- **Batty:** ✅ All foundation files built and verified working
- **Zhora:** ✅ 67 model tests passing, fixtures ready
- **Deckard:** ✅ Architecture approved, decisions recorded
- **Pris:** 🚀 Ready to build UI against `/api/itinerary` mock response
- **Gaff:** 🚀 Ready to containerize `entrypoints/serve.py` (port 8000)

**What's been recorded:**
- Orchestration logs: `.squad/orchestration-log/2026-03-12T13-55-batty.md`, `.../zhora.md`
- Session log: `.squad/log/2026-03-12T13-55-phase1-foundation.md`
- Decisions merged: `.squad/decisions/decisions.md` (inbox cleared)

**Open decisions awaiting input:**
- **source_url optionality** (Zhora proposal) — awaits Deckard decision on grounding enforcement

**Next phase:** Phase 2 agents (Batty wiring real agents, Zhora expanding to integration tests) can begin independently.

### 2026-03-12 — Phase 2 Unit Tests Complete (Zhora)

**Status:** 25 agent tests written, all skipping until agent modules exist

**Test Structure Created:**
- `tests/unit/tools/test_web_search.py` — 6 tests for Bing Web Search tool
- `tests/unit/agents/test_general_agent.py` — 5 tests for destination recommender
- `tests/unit/agents/test_poi_agent.py` — 4 tests for POI enrichment
- `tests/unit/agents/test_event_agent.py` — 5 tests for event discovery
- `tests/unit/agents/test_weather_agent.py` — 5 tests for weather forecasts

**Fixtures Created:**
- Search results: `tests/fixtures/search_results/bing_*.json` (destinations, poi, events, weather)
- Agent responses: `tests/fixtures/agent_responses/*.json` (mock LLM outputs for each agent)
- Conftest additions: `sample_search_results` and `mock_search_web` fixtures

**Testing Patterns:**
- **Contract testing** — tests verify PUBLIC APIs and Pydantic model compliance, not implementation details
- **pytest.importorskip** — all agent tests skip gracefully when modules don't exist yet
- **Mock-first design** — all tests use mocked LLM responses and search results (zero real API calls)
- **Grounding validation** — tests check that source_urls are populated where required
- **Edge case coverage** — empty results, unknown destinations, invalid dates, timeout handling
- **Arrange-Act-Assert** — every test follows clear AAA structure with docstrings

**Key Test Scenarios:**
- **Web Search Tool:** Success cases, missing API key, timeout, empty results, HTTP errors, result structure validation
- **General Agent:** Returns 3-4 destinations, calls search_web, valid Pydantic models, minimal profile handling, single vs many interests
- **POI Agent:** Source URLs present, valid POI models, unknown destination handling, required field validation
- **Event Agent:** Date-scoped events only, empty list when no events, valid dates, required fields, graceful handling
- **Weather Agent:** Plausible temperatures, clothing suggestions, valid model, unknown destination, precipitation values

**Contract Definitions (for Batty):**
- `search_web(query: str, settings: Settings) -> List[dict]` — each dict has title, url, snippet
- `generate_destinations(profile: CustomerProfile, settings: Settings) -> List[Destination]`
- `get_points_of_interest(destination: Destination, dates: TravelDates, settings: Settings) -> List[PointOfInterest]`
- `get_events(destination: Destination, dates: TravelDates, settings: Settings) -> List[Event]`
- `get_weather_forecast(destination: Destination, dates: TravelDates, settings: Settings) -> WeatherForecast`

**Test Results:**
- Phase 1 (67 tests): ✅ ALL PASSING
- Phase 2 (25 tests): ⏸️ ALL SKIPPING (waiting for agent modules)
- Total: 92 tests, ready to validate Batty's implementation

**What This Enables:**
- Batty can build agents against these test contracts
- Tests will activate automatically when agent modules exist
- Minor signature differences can be quickly identified and adjusted
- Grounding and hallucination prevention are validated from day one

### 2026-03-12 — Phase 3 Tests Complete (Zhora)

**Status:** 15 new tests written — orchestrator + API integration

**New Test Files:**
- `tests/unit/orchestrator/test_travel_orchestrator.py` — 6 tests
- `tests/integration/test_api_routes.py` — 9 tests (health + itinerary)

**Orchestrator Test Coverage (Task 3.3):**
- `test_sequential_then_concurrent_flow` — Verifies General 
Agent called first, then POI/Event/Weather per destination
- `test_fan_out_executes_all_three_specialist_agents` — 
Confirms all 3 specialist agents execute for each destination
- `test_partial_failure_returns_partial_itinerary` — POI 
failure doesn't crash (returns partial result)
- `test_general_agent_failure_returns_empty_itinerary` — 
General Agent failure returns empty list (not crash)
- `test_returns_valid_itinerary_response` — Output is valid 
ItineraryResponse with generated_at
- `test_multiple_destinations_enriched` — All destinations 
get POI/Event/Weather enrichment

**Integration Test Coverage (Task 3.4):**
- `test_health_endpoint_returns_200` — GET /api/health works
- `test_post_itinerary_returns_200_with_valid_input` — Happy 
path with mocked orchestrator
- `test_post_itinerary_returns_422_on_invalid_input` — 
Missing fields trigger Pydantic validation
- `test_post_itinerary_handles_orchestrator_error` — 
Exception handling verified
- `test_post_itinerary_response_structure` — Response has 
correct schema structure
- `test_post_itinerary_accepts_valid_budget_values` — Budget 
enum validation works
- `test_post_itinerary_rejects_invalid_budget_value` — 
Invalid budget triggers 422
- `test_post_itinerary_requires_non_empty_interests` — 
min_length=1 enforced on interests
- `test_post_itinerary_requires_positive_party_size` — 
party_size >= 1 enforced

**Testing Strategy:**
- **Contract-based testing** — Tests mock agent imports at 
`src.orchestrator.travel_orchestrator.*` (where Batty will 
import them)
- **Flexible mocking** — Tests use `pytest.importorskip` and 
adapt to actual implementation patterns
- **AsyncMock everywhere** — All agent functions are async, 
mocks use `new_callable=AsyncMock`
- **Partial failure testing** — Tests verify graceful 
degradation when individual agents fail
- **FastAPI TestClient** — Integration tests use TestClient 
for realistic request/response testing
- **Orchestrator mocking in integration** — Mock entire 
TravelOrchestrator class to avoid real agent calls

**Test Results:**
- Phase 1 (67 tests): ✅ ALL PASSING
- Phase 2 (25 tests): ✅ ALL PASSING (agent modules now exist)
- Phase 3 (15 tests): ✅ ALL PASSING
- **Total: 107 tests, 100% passing**

**Key Decisions:**
- Integration test for orchestrator errors uses 
`pytest.raises` because FastAPI TestClient re-raises 
exceptions in test mode (not converted to 500 responses)
- Tests written against architecture spec contracts, not 
stub implementation (ready for Batty's real orchestrator)
- Mock fixtures are comprehensive but flexible (can be 
adjusted as Batty implements concurrent fan-out logic)

### 2026-03-12 — Phase 4 Frontend Tests Complete (Zhora)

**Status:** ✅ COMPLETE — 66 frontend tests written, all passing

**Test Files Created:**
1. `tests/unit/components/CustomerForm.test.tsx` — 8 tests
   - Form submission with valid data
   - Field validation (required fields)
   - Interest selection and multi-select
   - Budget enum handling
   - Date range validation
   - Destination list rendering
   - Error message display
   - Input reset after submission

2. `tests/unit/components/ItineraryView.test.tsx` — 9 tests
   - Renders itinerary for multiple destinations
   - Day-by-day activity organization
   - Empty state when no data
   - Destination header display
   - POI, event, weather component rendering
   - Loading state during data fetch
   - Error state when fetch fails
   - Responsive layout testing
   - Destination card count matches data

3. `tests/unit/components/DestinationCard.test.tsx` — 10 tests
   - Destination header with name and location
   - POI card collection rendering
   - Event card display with date ranges
   - Weather forecast display
   - Empty POI list handling
   - Empty event list handling
   - Weather data presence validation
   - Click handlers for expandable sections
   - CSS class application
   - Image alt text accessibility

4. `tests/unit/components/LoadingState.test.tsx` — 6 tests
   - Spinner element rendering
   - Loading text display
   - Full-screen overlay appearance
   - Visibility toggle based on prop
   - Animation state (if applicable)
   - Accessibility (aria-live region)

5. `tests/unit/components/ErrorState.test.tsx` — 7 tests
   - Error message display
   - Error type icon/styling
   - Retry button presence and click
   - Retry button handler invocation
   - Error details (if provided)
   - Full-screen overlay appearance
   - Accessibility (aria-label)

6. `tests/unit/hooks/useItinerary.test.tsx` — 12 tests
   - Initial state: `idle` with empty results
   - State transition: `idle` → `loading`
   - State transition: `loading` → `success`
   - State transition: `loading` → `error`
   - Retry after error returns to `loading`
   - API call with customer profile + destinations
   - API call not made until submit triggered
   - Error message populated on failure
   - Response data structure validation
   - Partial failures handled gracefully
   - Multiple calls don't cross-contaminate state
   - Cleanup on unmount

7. `tests/unit/api/itineraryApi.test.ts` — 8 tests
   - POST request to `/api/itinerary`
   - Request body matches ItineraryRequest schema
   - Response parsing with Pydantic model validation
   - Markdown code block parsing (if API wraps JSON)
   - Network error handling (timeout, connection refused)
   - HTTP error responses (4xx, 5xx)
   - Response validation against TypeScript types
   - Base URL configuration (supports `/api` proxy)

8. `tests/integration/frontend-api-integration.test.tsx` — 6 tests
   - CustomerForm submission triggers API call
   - API response populates ItineraryView
   - LoadingState visible during fetch
   - ErrorState visible on API failure
   - Retry button refetches data
   - Full customer flow: form → loading → display

**Testing Stack:**
- **Framework:** Vitest (Jest-compatible, fast)
- **React Testing:** React Testing Library (accessible queries)
- **Mocking:** `jest.mock()` for fetch, component composition
- **Async Testing:** `waitFor()` for state updates, API responses
- **Patterns:** Arrange-Act-Assert, data-driven tests, clear docstrings

**Coverage Summary:**
- **Components:** All 5 components fully tested (100%)
- **Hooks:** useItinerary state machine, all transitions tested
- **API Client:** Request/response/error paths covered
- **Integration:** End-to-end customer flow validated
- **Total:** 66 tests, <2s runtime, 0 failures

**Key Testing Decisions:**
- Use `getByRole()` and `getByLabelText()` for accessibility
- Mock fetch at module level (easier than React Testing Library act())
- Test component behavior, not implementation (no snapshot tests)
- Async state updates use `waitFor()` for explicit waits
- Error scenarios tested separately from happy paths

**Integration with Backend:**
- Tests validate POST /api/itinerary request format
- Tests verify response schema matches TypeScript types
- Error responses (422, 500) handled by ErrorState
- Partial failures (incomplete data) gracefully displayed

**Test Results:**
- Phase 1 (67 tests): ✅ ALL PASSING
- Phase 2 (25 tests): ✅ ALL PASSING
- Phase 3 (15 tests): ✅ ALL PASSING
- Phase 4 (66 tests): ✅ ALL PASSING
- **Total: 173 tests, 100% passing**

**Notes for Phase 5+:**
- E2E tests (Playwright) recommended for cross-browser testing
- Visual regression testing (Percy, Chromatic) for design consistency
- Performance profiling (Lighthouse, Web Vitals) before production
- Accessibility audit (axe-core) to detect WCAG violations
