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
- **Gaff:** Infrastructure and deployment (Azure Bicep, containerization, CI/CD)

---

### 2026-03-12 — Phase 1 Backend Foundation Ready (Team)

**Status:** Backend code ready for containerization. Entrypoint defined.

**What Gaff should know:**
- **Docker target:** `entrypoints/serve.py` — the Uvicorn server entrypoint
- **Port:** Listens on port 8000
- **Environment variables:** See `.env.template` (Azure OpenAI, Bing Search keys, APP_VERSION)
- **Python version:** Check `requirements.txt` for dependencies (fastapi, uvicorn, pydantic-settings, etc.)
- **CMD suggestion:** `python entrypoints/serve.py` or `uvicorn src.api.app:create_app --host 0.0.0.0 --port 8000`
- **Health check:** `GET /api/health` (returns 200 with status JSON)

**Infrastructure next steps:**
- Bicep modules in `infra/` are approved (see Deckard's decisions for Azure resources: Container Apps, OpenAI, Bing Search)
- No Key Vault in MVP — secrets as Container App env vars
- Frontend can use Container Apps or Azure Static Web Apps (decision deferred)

**Reference Document:** `docs/architecture.md` (37KB, comprehensive MVP architecture)

**What This Means for Gaff:**
- Event Agent is a dedicated service within the agent framework
- Fan-out execution in concurrent phase with POI/Weather agents
- Must implement search-grounded reasoning for event discovery
- Inputs: destination, travel dates; Output: relevant events/festivals with details
- No authentication or persistence in MVP scope
