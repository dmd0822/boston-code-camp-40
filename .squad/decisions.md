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

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
