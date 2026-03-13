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
- **Batty:** Implement backend services and agent orchestration
- **POI Agent:** Points of interest discovery and recommendations
- **Event Agent:** Festival and special event integration
- **Weather Agent:** Historical weather data and climate insights
- **Grounding:** All agents use shared `src/agents/tools/web_search.py` tool

**Reference Document:** `docs/architecture.md` (37KB, comprehensive MVP architecture)

**What This Means for Batty:**
- Backend infrastructure is defined; ready to implement FastAPI service
- Agent orchestration pattern is set; implement two-phase execution in orchestrator
- Web search tool is part of agent implementation; all agents must use it
- No authentication or persistence in MVP scope

### 2026-03-12 — Phase 1 Foundation Complete (Batty)

**What was built:**
- Pydantic models in `src/api/models/` — CustomerProfile, TravelDates, Destination, PointOfInterest, Event, EventDates, WeatherForecast, ItineraryResponse
- Settings via `pydantic-settings` in `src/config/settings.py` — reads Azure OpenAI, Bing Search, and APP_VERSION from env vars (Optional for Phase 1 stub)
- FastAPI app factory in `src/api/app.py` with CORS middleware (allow_origins=["*"] for MVP)
- Health route: `GET /api/health` → `{"status": "healthy", "version": "0.1.0"}`
- Itinerary route: `POST /api/itinerary` → returns mock Lisbon+Porto data matching full schema
- Stub orchestrator in `src/orchestrator/travel_orchestrator.py` — `TravelOrchestrator.generate_itinerary()` returns mock data; ready for Phase 2 agent wiring
- Uvicorn entrypoint in `entrypoints/serve.py` with sys.path fix for project-root imports
- `.env.template` showing all required env vars
- `requirements.txt` updated with fastapi, uvicorn, pydantic-settings, httpx, agent-framework stack

**Patterns established:**
- App factory pattern (`create_app()`) for testability — integration tests can create isolated instances
- `get_settings()` cached via `@lru_cache` — single settings instance per process
- Models are the shared contract between API and orchestrator — both import from `src.api.models`
- `entrypoints/serve.py` adds project root to `sys.path` so imports resolve from any working directory
- Settings fields are Optional in Phase 1 (no Azure creds needed for mock data); will become required in Phase 2

**Key file paths:**
- `src/api/models/customer.py` — input schema
- `src/api/models/itinerary.py` — output schema
- `src/api/app.py` — app factory
- `src/api/routes/health.py` — health endpoint
- `src/api/routes/itinerary.py` — itinerary endpoint
- `src/orchestrator/travel_orchestrator.py` — orchestrator stub
- `src/config/settings.py` — env-based config
- `entrypoints/serve.py` — uvicorn runner

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

### 2026-03-12 — Phase 2 Agent Layer Complete (Batty)

**What was built:**
- **Web Search Tool** (`src/agents/tools/web_search.py`) — Bing Web 
  Search API wrapper with graceful error handling. Returns 
  structured results (title, url, snippet). Handles missing creds, 
  timeouts, rate limits without crashing.
- **System Prompts** (`data/prompts/*/system.md`) — 4 prompts (
  general, POI, event, weather) with mandatory search-first 
  instruction, citation requirements, and anti-hallucination rules.
- **General Agent** (`src/agents/general_agent.py`) — Destination 
  matching. Takes CustomerProfile, returns 3-4 destinations with 
  rationale grounded in web search.
- **POI Agent** (`src/agents/poi_agent.py`) — Points of interest 
  discovery. Returns 5-8 POIs per destination with categories, 
  visit duration, source URLs.
- **Event Agent** (`src/agents/event_agent.py`) — Festival/event 
  discovery. Date-scoped to travel window. Returns empty list if 
  no events match (NEVER fabricates).
- **Weather Agent** (`src/agents/weather_agent.py`) — Historical 
  weather forecasting. Returns avg temps, precipitation, clothing 
  suggestions based on web search for historical data.
- **Verification Script** (`scripts/verify_agents.py`) — Structure 
  and import verification for all agents.
- Updated `requirements.txt` with `pytest-asyncio` for async agent 
  testing.

**Patterns established:**
- All agents use Microsoft Agent Framework `Agent` class with 
  `AzureAIClient` from `agent-framework-azure-ai`
- System prompts stored in `data/prompts/{agent-name}/system.md` 
  (NOT in Python source)
- Factory pattern: `create_{agent}_agent(settings)` returns 
  configured Agent
- High-level API: `recommend_destinations()`, 
  `find_points_of_interest()`, `find_events()`, 
  `get_weather_forecast()` — async functions that create agent, 
  run query, parse/validate response
- JSON response parsing with markdown code block extraction (
  handles ```json blocks)
- Pydantic validation of all LLM outputs
- Graceful error handling: missing credentials → clear ValueError, 
  malformed LLM output → empty list/None
- `@tool` decorator from agent-framework for tool registration
- Tools receive Settings via dependency injection or get_settings()

**Key architectural decisions:**
- **Search-first grounding**: Every agent MUST call search_web 
  before answering. System prompts enforce this.
- **Citation enforcement**: All POIs, events, weather forecasts 
  must include source_url from search results.
- **No fabrication policy**: If web search insufficient, return 
  empty list/None. NEVER invent data.
- **Async by default**: All agent functions are async (enables 
  concurrent orchestration in Phase 3)
- **Graceful degradation**: Missing Bing API creds → empty search 
  results with warning. Missing Azure OpenAI creds → ValueError on 
  agent creation (fail fast).

**Key file paths:**
- `src/agents/tools/web_search.py` — Bing search tool
- `src/agents/general_agent.py` — Destination matching
- `src/agents/poi_agent.py` — POI discovery
- `src/agents/event_agent.py` — Event discovery
- `src/agents/weather_agent.py` — Weather forecasting
- `src/agents/__init__.py` — Agent exports
- `data/prompts/{agent-name}/system.md` — System prompts (4 files)
- `scripts/verify_agents.py` — Verification script

**Next phase:** Phase 3 orchestration (wire agents into 
TravelOrchestrator with sequential General → concurrent POI/Event/
Weather).

### 2026-03-12 — Phase 3 Orchestration Complete (Batty)

**What was built:**
- **Real TravelOrchestrator** (
  `src/orchestrator/travel_orchestrator.py`) — Replaced stub 
  with full two-phase agent coordination. Takes Settings in 
  __init__, implements sequential General Agent call followed by 
  concurrent POI/Event/Weather enrichment for each destination.
- **Settings Dependency Injection** (
  `src/api/routes/itinerary.py`) — Updated route to inject 
  Settings via FastAPI Depends(), creates fresh orchestrator per 
  request.
- **Error Handling Pattern** — `_safe_call()` wrapper catches 
  specialist agent failures and returns defaults (empty list or 
  None). General Agent failures return empty itinerary, NOT 500.
- **Concurrent Fan-Out/Fan-In** — Uses `asyncio.gather()` for 
  parallel specialist agent calls per destination, merges results 
  back into Destination objects.

**Patterns established:**
- **Two-phase orchestration**: Sequential General Agent → 
  concurrent specialist agents (one fan-out per destination)
- **Graceful degradation**: Specialist failures → partial data (
  empty POIs/events, None weather). General failure → empty 
  itinerary with 200 status.
- **Per-request orchestrator**: Created fresh in route handler 
  with injected Settings (stateless, testable)
- **TypeVar for generic safe call**: `_safe_call()` uses TypeVar 
  to preserve type hints for any agent function signature
- **Logging over crashing**: All failures logged at warning/error 
  level; no exceptions propagate to FastAPI

**Architecture compliance:**
- ✅ Sequential Phase 1 (General Agent)
- ✅ Concurrent Phase 2 (POI/Event/Weather per destination)
- ✅ Settings injected via FastAPI dependency
- ✅ No fabricated data on agent failure
- ✅ All lines ≤79 chars, type hints, PEP 257 docstrings
- ✅ No retries implemented (kept simple for MVP; can add later)

**Key file paths:**
- `src/orchestrator/travel_orchestrator.py` — Real orchestrator
- `src/api/routes/itinerary.py` — Route with DI

**Testing readiness:**
- Orchestrator is fully unit-testable (inject mock Settings)
- Route is integration-testable (use FastAPI TestClient with 
  override_dependency)
- All agent calls wrapped in try/except with sensible defaults

**What's now possible:**
- End-to-end itinerary generation with real LLM calls
- Partial results when some agents fail (better UX than 500)
- Concurrent enrichment reduces latency (3 agents run in 
  parallel per destination)

**Next phase:** Phase 4 integration testing (Zhora) or Phase 5 
containerization (Gaff).

### 2026-03-13 — Phase 6.1 Error Handling Hardening (Batty)

**Architecture decisions:**
- Added a shared backend exception hierarchy in `src/exceptions.py` 
  so routes, agents, and the orchestrator can map failures to stable 
  HTTP statuses without duplicating error translation logic.
- Standardized API failures through `src/api/error_handlers.py` and 
  `src/api/app.py`, using one JSON envelope for validation, timeout, 
  configuration, and unexpected server errors.
- Tightened orchestration semantics in 
  `src/orchestrator/travel_orchestrator.py`: specialist failures still 
  degrade to partial results, but all-specialist failure now raises a 
  hard error and General Agent failures propagate to the API layer.

**Patterns established:**
- Use `run_agent_prompt()` and `parse_json_payload()` from 
  `src/agents/agent_utils.py` to enforce Azure OpenAI timeouts, empty 
  response checks, markdown fence stripping, and JSON parsing.
- Use `AgentCallResult` in the orchestrator to distinguish a genuine 
  empty result from a fallback caused by agent failure.
- Keep Bing Search resilient in `src/agents/tools/web_search.py` by 
  loading fresh env-backed settings per call, applying explicit 
  `httpx.Timeout`, and returning `[]` on timeout, HTTP, request, or 
  JSON parsing errors.
- Put semantic request validation in Pydantic models: 
  `TravelDates` now rejects end-before-start, and `CustomerProfile` 
  trims/validates interests, departure city, and notes.

**User preferences learned:**
- Dave explicitly wanted robust backend hardening without changing the 
  frontend contract, plus verification with 
  `python -m pytest tests/ -x -q`.
- Backend errors should be explainable in human terms, logged for 
  debugging, and returned as safe JSON without stack traces.

**Key file paths:**
- `src/exceptions.py` — shared backend exception types
- `src/api/error_handlers.py` — structured JSON error envelope
- `src/api/routes/itinerary.py` — route-level error translation
- `src/api/models/customer.py` — itinerary input validation rules
- `src/agents/agent_utils.py` — shared Azure OpenAI timeout and 
  response parsing helpers
- `src/agents/tools/web_search.py` — Bing Search timeout handling
- `tests/integration/test_api_routes.py` — structured API error tests
- `tests/unit/api/test_models.py` — travel date order validation test

**Phase 6 Summary:**

Phase 6 completed with cross-team effort achieving 262 backend tests 
passing (4 skipped), 63 frontend tests passing, zero failures.

- **Phase 6.1 (Batty):** Error handling hardening across API routes, 
  agents, orchestrator, and web search tool. Structured JSON error 
  responses, graceful degradation, timeout handling, input validation, 
  comprehensive logging.
- **Phase 6.2 (Pris):** Loading UX polish with multi-step progress 
  indicator, CSS-only animations, skeleton loaders, error states, 
  transitions, full accessibility. Conference-demo ready.
- **Phase 6.3 (Zhora):** Error handling test coverage for API errors, 
  orchestrator degradation, agent failures, web search errors. 
  Comprehensive error scenario testing.

**Ready for Phase 7:** Performance optimization and monitoring.
