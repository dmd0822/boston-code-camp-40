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
- **Pris:** Build React frontend and integrate with backend API

---

### 2026-03-12 — Phase 1 Backend & Tests Complete (Team)

**Status:** Ready for frontend development. Backend API is live with realistic mock data.

**What Pris can do now:**
- **Endpoint ready:** `POST /api/itinerary` returns full mock Lisbon+Porto response with realistic schema
- **Health check:** `GET /api/health` for status monitoring
- **Mock data structure:** All Pydantic models defined; response matches final schema
- **No auth required:** MVP scope — build UI without authentication layer
- **Port:** Backend runs on port 8000 (set CORS `allow_origins` in code if narrowing from `["*"]`)

**API contract reference:**
- Input: `POST /api/itinerary` body with CustomerProfile (interests, budget, travel_dates) and destination list
- Output: Full ItineraryResponse with destinations → itineraries (days) → activities + POIs + events + weather
- Schema file: `src/api/models/itinerary.py` (check for latest fields)

**Frontend structure suggestion:**
- Mirror data structures in TypeScript (manual sync for MVP; auto-gen from OpenAPI is post-MVP)
- Form component for customer input (interests, budget, dates)
- Itinerary display with day-by-day activities, POI cards, events, weather

**Reference Document:** `docs/architecture.md` (37KB, comprehensive MVP architecture)

**What This Means for Pris:**
- POI Agent is a dedicated service within the agent framework
- Fan-out execution in concurrent phase with Event/Weather agents
- Must implement search-grounded reasoning for POI discovery
- Inputs: destination, interests; Output: points of interest list with descriptions
- No authentication or persistence in MVP scope
