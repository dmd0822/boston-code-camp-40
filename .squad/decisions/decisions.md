# Decisions

Central record of all architecture, design, and implementation decisions. Updated from inbox after each phase.

---

## 2026-03-12 — Agent Framework Integration Pattern

**Author:** Batty | **Status:** Implemented in Phase 2

Building Phase 2 agent layer using Microsoft Agent Framework (`agent-framework` package). Established consistent patterns for agent creation, system prompt storage, tool registration, response parsing, and error handling.

**Decision:**

### Agent Factory Pattern

Each agent module provides `create_{agent}_agent(settings: Settings) -> Agent` factory:
- Validates credentials (fail fast)
- Creates AzureAIClient
- Loads system prompt from `data/prompts/{agent}/system.md`
- Registers tools (search_web)
- Returns configured Agent

### High-Level Async API

Each agent module provides high-level async functions:
```python
async def {verb}_{noun}(inputs..., settings: Optional[Settings] = None) -> ReturnType:
    # Create agent, build user prompt, run agent
    # Parse JSON response (handle markdown code blocks)
    # Validate with Pydantic, return typed result
```

Examples: `recommend_destinations()`, `find_points_of_interest()`, `find_events()`, `get_weather_forecast()`

### System Prompts in Files

System prompts stored in `data/prompts/{agent-name}/system.md` (NOT in Python source). Loaded at agent creation time. Rationale: separates prompt engineering from code; enables prompt versioning without code changes.

### Tool Registration

Tools defined with `@tool` decorator from agent-framework and registered in Agent constructor as list.

### Response Parsing

LLMs may wrap JSON in markdown code blocks. Parse defensively to extract content, then validate with Pydantic models.

### Error Handling Strategy

- Missing Azure OpenAI credentials: Raise ValueError from factory (fail fast, clear message)
- Missing Bing Search credentials: Return empty results from search_web with warning log (graceful degradation)
- HTTP errors (timeout, 401, 429): Log error, return empty results
- JSON parse errors: Log error, return empty list/None
- Pydantic validation errors: Log warning, skip invalid items
- Unexpected exceptions: Log error, return empty list/None

All agent functions return empty list or None on error, NEVER raise to caller (except credential validation errors).

**Consequences:**
- Benefits: Consistent API across all agents, clear separation (factory vs execution), prompts managed separately, graceful error handling, type-safe outputs
- Trade-offs: Multiple layers add boilerplate, aggressive error suppression may hide dev issues, path resolution assumes project structure

---

## 2026-03-12 — Phase 3 Orchestration Pattern: Error Handling & Concurrency

**Author:** Batty | **Status:** Implemented

Implement two-phase orchestration with graceful degradation:
- **Phase 1 (Sequential):** General Agent failure → empty itinerary with 200 status
- **Phase 2 (Concurrent):** Specialist agent failures → partial data (empty lists, None)

**Rationale:**
- Better UX than cascading failures: if POI agent fails but Event/Weather succeed, user gets useful results
- Empty itinerary preferable to 500 error when General Agent unavailable
- Logs capture all failures for debugging without exposing to end user
- Concurrency reduces latency: 3 specialist agents run in parallel per destination (asyncio.gather)
- Settings injection enables testing: TravelOrchestrator takes Settings in __init__ (no global state)

**Implementation:**

Pattern: _safe_call wrapper
```python
async def _safe_call(agent_func, *args, default, **kwargs) -> T:
    try:
        return await agent_func(*args, **kwargs)
    except Exception as exc:
        logger.warning(f"Agent {agent_func.__name__} failed: {exc}. Using default: {default}")
        return default
```

Pattern: Concurrent enrichment per destination
```python
enriched_destinations = await asyncio.gather(
    *[self._enrich_destination(dest, profile.travel_dates)
      for dest in destinations]
)
```

**Consequences:**
- Positive: System resilient to partial failures, performance scales with concurrency, clear separation of concerns
- Negative: No retry logic in MVP, partial results may confuse users if not communicated in UI, no telemetry/metrics on agent failure rates

**Files modified:**
- `src/orchestrator/travel_orchestrator.py` — Full rewrite with _safe_call wrapper
- `src/api/routes/itinerary.py` — Added Settings DI

---

## 2026-03-12 — Async/Sync Contract: Test Against Actual Framework Behavior

**Author:** Zhora | **Status:** PROPOSED | **Decision Required:** Deckard or Batty

Phase 2 testing found mismatch between expected contract and implementation:
- Tests expect `search_web` synchronous: `results = search_web("query", settings)`
- Batty's implementation uses async Microsoft Agent Framework `@tool` decorator

Test results:
- 67 Phase 1 tests: ✅ PASSING (Pydantic models)
- 6 web search tests: ❌ FAILING (async/sync mismatch)
- 19 agent tests: ❌ FAILING (function naming mismatch or not yet implemented)

**Options:**

**Option A:** Make search_web synchronous
- Pros: Simpler to test, matches test contract
- Cons: Doesn't align with async FastAPI and Agent Framework patterns

**Option B:** Make tests async (RECOMMENDED)
- Pros: Aligns with async framework architecture
- Cons: Requires `pytest-asyncio` and `@pytest.mark.asyncio` decorators

**Option C:** Provide both sync and async wrappers
- Pros: Flexibility for different contexts
- Cons: Maintenance overhead, potential confusion

**Recommendation:** Option B — make tests async to match the framework's async-first architecture. Microsoft Agent Framework and FastAPI both expect async, so tests should validate the actual async contract.

Changes needed:
1. Add `pytest-asyncio` to requirements
2. Add `@pytest.mark.asyncio` to all web search tests
3. Change `results = search_web(...)` to `results = await search_web(...)`
4. Update conftest `mock_search_web` fixture to handle async

**Who needs to decide:** Deckard (architecture lead)

---

## 2026-03-12 — User Directive: Keep READMEs Updated Through Each Phase

**Author:** Dave Davis (via Copilot) | **Date:** 2026-03-12T14-48 | **Status:** Documented

User request captured for team memory: Keep all README files updated as work progresses through each phase.

---

## 2026-03-12 — Core Architecture: FastAPI + Agent Framework + ConcurrentBuilder

**Author:** Deckard | **Status:** Approved

We need a backend stack for the travel agent application orchestrating 4 AI agents using Microsoft Agent Framework.

**Decision:**
1. **FastAPI** — async-native HTTP layer with Pydantic models and auto-generated OpenAPI docs
2. **Microsoft Agent Framework** (`agent-framework`, `agent-framework-azure-ai`, `agent-framework-orchestrations`) — NOT Semantic Kernel
3. **Two-phase orchestration:** General Agent (sequential) → ConcurrentBuilder fan-out (POI, Event, Weather in parallel)
4. **Deterministic orchestrator** — plain Python control flow, not LLM-driven routing
5. **Stateless API** — no database, no auth (MVP scope)

**Impact:**
- All backend uses `agent-framework`, not Semantic Kernel/LangChain
- Agent code in `src/agents/`, API in `src/api/`, orchestration in `src/orchestrator/`
- All agents receive `search_web` tool (Bing Search) for grounding
- Pydantic models in `src/api/models/` are the single source of truth for data contracts

**Alternatives rejected:** Semantic Kernel (explicitly excluded), LLM-driven orchestration (too unpredictable), sequential-only agents (too slow).

---

## 2026-03-12 — Frontend Architecture: React + Vite + TypeScript SPA

**Author:** Deckard | **Status:** Approved

Choose frontend build tooling and repo structure.

**Decision:**
1. **React 18+ with TypeScript** — type safety matching backend Pydantic contracts
2. **Vite** — fast dev server, modern defaults
3. **Frontend in `frontend/` at repo root** — not inside Python `src/`
4. **Pure SPA, no SSR or Next.js** — backend is separate FastAPI service
5. **TypeScript interfaces manually synced with Pydantic** for MVP; auto-generation from OpenAPI is post-MVP

**Impact:**
- Frontend developers work in `frontend/`, backend in `src/`
- Frontend communicates exclusively via `POST /api/itinerary` and `GET /api/health`
- No shared code — independent deployables

---

## 2026-03-12 — Agent Grounding Strategy: Mandatory Bing Search

**Author:** Deckard | **Status:** Approved

All agents must be grounded in web search to reduce hallucination.

**Decision:**
1. **Bing Web Search API** — sole search tool for all agents
2. **Mandatory search-first** — system prompt includes "You MUST call search_web before answering"
3. **Cite sources** — every factual claim references a URL from search results
4. **Schema enforcement** — agent output parsed into Pydantic models; malformed output triggers retry (max 2)
5. **Empty over fabricated** — agents return empty lists rather than inventing data when search yields no results
6. **Agent prompts in `data/prompts/{agent-name}/system.md`** — version-controlled, reviewable in PRs

**Impact:**
- `src/agents/tools/web_search.py` is shared by all agents
- Every agent test must verify `search_web` was called
- Prompt changes are code changes (in repo)

---

## 2026-03-12 — Infrastructure: Azure Container Apps + Bicep

**Author:** Deckard | **Status:** Approved

Deployment target and infrastructure-as-code tooling.

**Decision:**
1. **Azure Container Apps** (Consumption tier) — both frontend and backend containers
2. **Azure Container Registry** (Basic) — Docker images
3. **Azure OpenAI** (S0) with GPT-4o deployment — LLM
4. **Bing Web Search** (Cognitive Services) — agent grounding
5. **Bicep modules in `infra/`** — modular design with separate `.bicep` files per resource type
6. **Parameter files for dev/prod** — environment-specific configs
7. **No Key Vault in MVP** — secrets as Container App env vars; Key Vault is post-MVP hardening

**Impact:**
- All Bicep in `infra/` with `main.bicep` as entry point
- Dockerfile in repo root builds backend container
- Frontend can use either Container Apps or Azure Static Web Apps (deferred to implementation)

---

## 2026-03-12 — Phase 1 Backend Foundation Patterns

**Author:** Batty | **Status:** Implemented

Backend foundation is live. Key patterns established for rest of project.

**Decision:**
1. **App factory** — `create_app()` in `src/api/app.py` returns fresh FastAPI instance; tests use this to avoid shared state
2. **Settings are Optional in Phase 1** — `AZURE_OPENAI_*` and `BING_SEARCH_*` default to `None` so stub runs without credentials; Phase 2 tightens to required fields
3. **Models are the contract** — API routes and orchestrator both import from `src.api.models`; schema changes sync automatically
4. **Mock data is realistic** — stub orchestrator returns Lisbon + Porto data matching full `ItineraryResponse` schema

**Deliverables:**
- Pydantic models: CustomerProfile, TravelDates, Destination, PointOfInterest, Event, EventDates, WeatherForecast, ItineraryResponse
- FastAPI app factory with CORS middleware
- Health route: `GET /api/health` → `{"status": "healthy", "version": "0.1.0"}`
- Itinerary route: `POST /api/itinerary` → mock Lisbon+Porto response
- Settings via pydantic-settings: reads Azure, Bing, version from env vars
- Stub orchestrator ready for Phase 2 agent wiring
- Uvicorn entrypoint: `entrypoints/serve.py`

**Who should care:**
- **Pris (Frontend):** Endpoint returns realistic mock data now; start building UI
- **Zhora (Tests):** App factory and models ready for unit/integration tests
- **Gaff (Infra):** `entrypoints/serve.py` is container CMD target (port 8000)

---

## 2026-03-12 — Phase 1 Test Suite Complete

**Author:** Zhora | **Status:** Implemented

Comprehensive test suite for all Pydantic models; 67 tests all passing.

**Decision & Findings:**

1. **Test Coverage:** 67 unit tests covering CustomerProfile, TravelDates, Destination, PointOfInterest, Event, EventDates, WeatherForecast, ItineraryResponse
2. **Shared Fixtures:** `tests/conftest.py` provides reusable valid/invalid test data for all models
3. **Testing Patterns:**
   - Use `deepcopy()` on fixture dicts before mutation (avoid cross-test contamination)
   - `pytest.mark.parametrize` for systematic negative testing per field
   - Arrange-Act-Assert via class-per-model organization
   - Every test has docstring explaining what it validates

4. **Discrepancies Found vs Architecture:**
   - **`source_url` is Optional** on POI, Event, WeatherForecast — architecture says grounding is mandatory; decision filed (see below)
   - **`interests` enforces `min_length=1`** — architecture didn't specify; good constraint
   - **`budget` uses regex enum** (`budget|moderate|luxury`) — architecture didn't specify; good constraint
   - **`generated_at` is required (no default)** — architecture implied auto-population
   - **`EventDates` as separate model from `TravelDates`** — same structure, different class; affects interop

**Impact:**
- Phase 2 tests will expand to integration suite covering orchestrator and agent calls
- Model discrepancies must be resolved before agent implementation

---

## 2026-03-12 — source_url Should Be Required on Grounded Models (PROPOSED)

**Author:** Zhora | **Status:** PROPOSED | **Decision Required:** Deckard

The architecture document states grounding is mandatory (every factual claim must cite a `source_url`). However, Batty's Pydantic models define `source_url` as `Optional[str] = Field(default=None)` on PointOfInterest, Event, and WeatherForecast.

**Problem:** Malformed agent output (missing citations) will pass schema validation silently. Grounding is only enforced at prompt level, which is inherently unreliable.

**Recommendation:**
- **Option 1 (Safer):** Make `source_url` required (`str`, not `Optional[str]`) so schema validation catches missing citations automatically
- **Option 2 (Current):** Accept current design and document that grounding enforcement is prompt-only (weaker guarantee)

Option 1 is preferred. If partial results need to omit URLs, use a separate "draft" model or sentinel value.

**Who needs to decide:** Deckard (architecture)

**Implications:** 
- If adopted, Batty updates models; Zhora updates test expectations; all agent implementations must ensure source_url is populated

---

---

## 2026-03-13 — Phase 6.1 Backend Error Handling Hardening

**Author:** Batty | **Status:** Implemented

Adopted a shared backend exception hierarchy in `src/exceptions.py` and mapped it to one structured JSON error envelope in `src/api/error_handlers.py`.

**Rules:**
- API routes return one error shape: `{"error": {...}, "detail": "..."}`.
- Request validation failures return HTTP 422 with structured field details.
- Azure OpenAI timeouts return HTTP 504 via `ExternalServiceTimeoutError`.
- Upstream Azure/Bing failures return safe 5xx responses without stack traces in the body.
- Specialist agent failures degrade to partial itinerary data; all specialists failing raises `ItineraryGenerationError`.
- General Agent failures propagate to the API layer instead of silent empty itinerary.

**Impacted Files:**
- `src/exceptions.py`
- `src/api/error_handlers.py`
- `src/api/routes/itinerary.py`
- `src/orchestrator/travel_orchestrator.py`
- `src/agents/agent_utils.py`
- `src/agents/tools/web_search.py`

---

## 2026-03-13 — Phase 6.2 Loading UX Polish

**Author:** Pris | **Status:** Implemented

Frontend loading experience enhanced with deterministic staged progress model and CSS-only animations.

**Decision:**
- Represent backend progress with staged frontend model (destination matching → enrichment → finalizing)
- Keep implementation lightweight: CSS-only animation, skeleton placeholders, `prefers-reduced-motion` support
- Retry replays last submitted `CustomerProfile` from `useItinerary`

**Why This Works:**
- Users get meaningful progress feedback before live streaming exists
- UI reflects actual orchestration shape instead of generic spinner
- Retry preserves momentum during demos

**Files Modified:**
- `src/frontend/src/components/LoadingState/`
- `src/frontend/src/components/ErrorState/`
- `src/frontend/src/hooks/useItinerary.ts`
- `src/frontend/src/components/ItineraryView/`

---

## 2026-03-13 — Phase 6.3 Error Test Coverage Contract

**Author:** Zhora | **Status:** Implemented

Typed backend exceptions plus standard API error envelope as test contract.

**Contract in Tests:**
- API errors return JSON: `detail`, `error.code`, `error.message`, `error.details[]`
- Validation failures → `validation_error` with structured field-level details
- Route-level failures → `itinerary_generation_error`
- Timeout paths → `external_service_timeout`
- Orchestrator distinguishes: single specialist failure (partial results) vs General Agent failure (service error) vs all specialist failures (generation error)

**Impact:** Tests provide concrete backend error contract safe for frontend consumption, avoid stack trace leakage, align route/orchestrator/agent/web-search error strategy.

---

## 2026-03-28 — Travel Advisory Agent Integration

**Author:** Batty | **Status:** Implemented | **Issue:** #4

Added a fifth specialist agent — Travel Advisory Agent — to the Phase 2 concurrent fan-out. It runs alongside POI, Event, and Weather agents via `asyncio.gather()`.

**Decision:**

1. **Optional[TravelAdvisory]** on Destination (not List) — a destination has one advisory per country, not multiple. Follows Weather Agent's Optional pattern, not the POI/Event list pattern.

2. **source_url is required** (not Optional) — advisory data without a verifiable source is useless. `specific_warnings` also has `min_length=1` since every advisory has at least one concern.

3. **advisory_level validated 1-4** — uses Pydantic `ge=1, le=4` to enforce the State Department scale at the model boundary.

4. **Graceful degradation** — advisory failure returns None, does not block other agents. The all-specialist-failure check now requires all four agents (not three) to fail before raising ItineraryGenerationError.

**Impact:**
- **Pris (Frontend):** Destination response now includes `travel_advisory: {...} | null`. UI can display advisory badge.
- **Zhora (Tests):** New agent needs unit tests (fixtures may already exist at `tests/fixtures/agent_responses/travel_advisory_agent.json`).
- **Gaff (Infra):** No new services required — uses same Azure OpenAI and Bing Search as existing agents.

---

## 2026-03-28 — Travel Advisory UI Pattern

**Author:** Pris | **Status:** Implemented | **Issue:** #4

Travel advisory data is optional on every `Destination` object (`travel_advisory?: TravelAdvisory | null`). The frontend degrades gracefully when it's missing.

**UI Levels:**

| Level | Badge | Card Behavior |
|-------|-------|---------------|
| 1 🟢 | Green inline badge | Normal display |
| 2 🟡 | Yellow inline badge | Normal display |
| 3 🟠 | Orange badge + expanded warning panel | `role="alert"` panel with specific warnings |
| 4 🔴 | Red badge + expanded warning panel | Panel + "choose alternate destination" advice |

**Top-Level Banner:**

`ItineraryView` filters for Level 3-4 destinations and renders a `⚠️ Travel Advisory Warnings` banner above all destination cards. This ensures severe advisories are never buried.

**Loading Step:**

The `LoadingState` now includes "Checking travel advisories..." in Phase 2 (concurrent with POI/events/weather agents).

**Impact:**
- **Batty:** Backend must include `travel_advisory` in the `Destination` response model (nullable/optional).
- **Zhora:** New component has 24 tests. Additional edge-case tests may be warranted for the ItineraryView banner.
- **Gaff:** No infra changes needed.

---

## 2026-03-28 — Date Picker Defaults (Pris)

**Author:** Pris | **Status:** Implemented

When the traveler picks a start date, the form now only auto-updates the end date if the current end date is blank or earlier than the new start date. If the traveler already chose a later valid end date, the form preserves it.

**Reasoning:** This keeps the new convenience behavior from overwriting an intentional return date. The end date input also uses the current start date as its native `min` constraint so invalid earlier selections are blocked in the browser UI.

---

## 2026-03-28 — User Directive: Web Search Enabled (Dave Davis)

**Author:** Dave Davis | **Status:** Implemented | **Date:** 2026-03-23

All agents should have web search enabled — use `web_search` and `web_fetch` tools to look up documentation, verify facts, and ground decisions in current information.

**Why:** User request — captured for team memory

---

## 2026-03-28 — Travel Advisory Agent Test Contracts

**Author:** Zhora | **Status:** Implemented | **Issue:** #4

Tests for the Travel Advisory Agent follow the same patterns as Weather Agent tests:
- `_patch_agent_pipeline()` helper encapsulates all Azure mocking
- `pytest.importorskip()` used for graceful skipping if module doesn't exist
- Mock fixtures in `tests/fixtures/agent_responses/travel_advisory_agent.json`
- Hallucination tests validate `travel.state.gov` grounding

**Impact:**

- **Batty:** Implementation must return `TravelAdvisory` model with `advisory_level` (1-4), `advisory_summary`, `specific_warnings` (non-empty list), and `source_url` (containing `travel.state.gov`). Return `"null"` string for unknown destinations.
- **Orchestrator:** `get_travel_advisory` is now part of Phase 2 fan-out alongside POI/Event/Weather. Tests verify it's called once per destination and degrades gracefully on failure.
- **Model:** `TravelAdvisory.advisory_level` uses `ge=1, le=4`; `specific_warnings` uses `min_length=1`; `last_updated` is optional.

---

## How to Use This Document

- **Adding decisions:** File them in `.squad/decisions/inbox/` (named `{author}-{topic}.md`). Scribe merges to this file after each phase.
- **Referencing decisions:** Link to section headers, e.g., "See **Core Architecture** decision for agent framework details."
- **Revising decisions:** Add new decision if status changes (e.g., "APPROVED" → "REVISED"), mark old one obsolete.
- **Archiving:** Old entries (>30 days) move to `decisions-archive.md` to keep this file <20KB.
