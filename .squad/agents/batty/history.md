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
