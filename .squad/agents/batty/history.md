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
