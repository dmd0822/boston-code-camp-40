# Squad Decisions

## Active Decisions

### 2026-03-12 — Travel Agent MVP Architecture

**Status:** APPROVED

**Backend Stack:**
- Framework: Microsoft Agent Framework (`agent-framework` package, NOT Semantic Kernel)
- HTTP API: FastAPI (async-native, Pydantic models)
- LLM: Azure OpenAI (GPT-4o via `agent-framework-azure-ai`)
- Web Search: Bing Web Search API (custom tool in `src/agents/tools/web_search.py`)

**Agent Design:**
- 4 agents: General (destination matching), POI (points of interest), Event (festivals/fairs), Weather (historical forecasts)
- Orchestration: Two-phase deterministic Python (NOT LLM-driven)
  - Phase 1: Sequential invocation of General Agent
  - Phase 2: Fan-out concurrent execution of POI/Event/Weather agents
- Grounding: Mandatory web search for all agents (search-first pattern)

**API Design:**
- Endpoint: `POST /api/itinerary` (accepts customer profile, returns itinerary)
- Health: `GET /api/health` (liveness check)
- Models: Pydantic schemas in `src/api/models/`

**Frontend:**
- Framework: React + Vite + TypeScript
- Location: `frontend/` at repo root (separate from Python `src/`)
- Pattern: SPA with form input → itinerary display

**Infrastructure:**
- Platform: Azure Container Apps
- IaC: Bicep in `infra/` with modular `.bicep` files
- Services: Azure OpenAI, Azure Container Registry, Bing Search API

**Scope (MVP):**
- NO authentication
- NO itinerary persistence
- NO payment/booking integration

**Prompts:**
- System prompts stored in `data/prompts/{agent-name}/system.md` per existing repo convention

**Document Reference:**
- `docs/architecture.md` — single source of truth for all architectural decisions

### 2026-03-28 — Advisory visualization uses dedicated panel for all levels

**Status:** ✅ APPROVED & IMPLEMENTED

**Decision:**

Created a new `TravelAdvisoryPanel` component that renders for **all advisory levels** (not just severe), giving every destination full advisory context including a CSS-only risk gauge, specific warnings, source attribution, and timestamp.

- `TravelAdvisoryBadge` remains the inline badge in the DestinationCard header
- `TravelAdvisoryPanel` is the dedicated detailed view shown below the header
- No external charting/animation libraries — pure CSS gauge with gradients and opacity transforms
- `role="meter"` for the gauge, `role="alert"` for Level 3-4, `role="region"` for Level 1-2

**Why:** Previous `TravelAdvisoryBadge` only showed expanded view for Level 3-4 advisories. Dedicated panel ensures all destinations render full advisory context.

**Impact Across Team:**

- **Batty (Backend):** No changes — existing `TravelAdvisory` Pydantic model unchanged
- **Zhora (QA):** 29 new tests; frontend test suite now at 120 total
- **Gaff (Infra):** No infrastructure changes
- **Deckard (Architecture):** Follows established CSS Modules pattern; zero new dependencies

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
