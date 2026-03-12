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

### 2026-03-12 — Architecture Design Complete

- **Architecture doc:** `docs/architecture.md` — the single source of truth for the entire system design.
- **Backend pattern:** FastAPI (async) + Microsoft Agent Framework (`agent-framework` package, NOT Semantic Kernel). Orchestrator is deterministic Python, not LLM-driven.
- **Orchestration:** Two-phase — General Agent (sequential) → ConcurrentBuilder fan-out to POI/Event/Weather agents. Uses `agent-framework-orchestrations` package.
- **Grounding:** All agents use Bing Web Search via shared `search_web` tool in `src/agents/tools/web_search.py`. Mandatory search-first pattern.
- **Prompts:** Stored in `data/prompts/{agent-name}/system.md` per existing repo convention.
- **API:** Two endpoints — `POST /api/itinerary` and `GET /api/health`. Pydantic models in `src/api/models/`.
- **Frontend:** React + Vite + TypeScript in `frontend/` at repo root (separate from Python `src/`).
- **Infra:** Azure Container Apps + Azure OpenAI + Bing Search. Bicep in `infra/` with modular `.bicep` files.
- **Key files:**
  - `docs/architecture.md` — architecture document
  - `src/agents/` — agent implementations
  - `src/api/` — FastAPI application
  - `src/orchestrator/` — travel orchestrator
  - `frontend/` — React SPA
  - `infra/` — Bicep modules
  - `data/prompts/` — agent system prompts
- **Decisions written to:** `.squad/decisions/inbox/deckard-core-architecture.md`, `deckard-frontend-architecture.md`, `deckard-grounding-strategy.md`, `deckard-infrastructure.md`
- **User preference:** Dave wants Microsoft Agent Framework specifically (not Semantic Kernel). Agents must be grounded in web search. MVP scope is strict — no auth, no persistence.
