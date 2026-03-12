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
