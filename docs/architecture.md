# Travel Agent Application — Architecture

> **Status:** Approved (MVP)
> **Author:** Deckard (Lead/Architect)
> **Date:** 2026-03-12
> **Scope:** MVP — no authentication, no itinerary persistence

---

## Table of Contents

📊 **[Visual Architecture Diagrams](diagrams.md)** — Mermaid diagrams for all system components

1. [System Overview](#1-system-overview)
2. [Backend Architecture](#2-backend-architecture)
3. [Agent Design](#3-agent-design)
4. [API Design](#4-api-design)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Infrastructure](#6-infrastructure)
7. [Data Flow](#7-data-flow)
8. [Testing Strategy](#8-testing-strategy)
9. [Project Structure](#9-project-structure)
10. [Implementation Priority](#10-implementation-priority)

---

## 1. System Overview

### High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│  (Vite + TypeScript — customer form, itinerary display)         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS (REST JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Orchestrator Service                          │  │
│  │                                                           │  │
│  │  1. Receive customer profile                              │  │
│  │  2. Invoke General Agent (sequential)                     │  │
│  │  3. Fan-out to POI / Event / Weather agents (concurrent)  │  │
│  │  4. Fan-in: aggregate results into itinerary              │  │
│  │  5. Return itinerary to frontend                          │  │
│  └───────────┬──────────┬──────────┬──────────┬──────────────┘  │
│              │          │          │          │                  │
│       ┌──────▼───┐ ┌───▼────┐ ┌──▼────┐ ┌──▼──────┐           │
│       │ General  │ │  POI   │ │ Event │ │ Weather │           │
│       │  Agent   │ │ Agent  │ │ Agent │ │  Agent  │           │
│       └──────┬───┘ └───┬────┘ └──┬────┘ └──┬──────┘           │
│              │         │         │         │                    │
│              ▼         ▼         ▼         ▼                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          Azure OpenAI  +  Bing Web Search API             │  │
│  │          (LLM reasoning)   (grounding / web search)       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Principles

- **Agent boundaries are explicit.** Each agent has a defined
  contract (inputs, outputs, system prompt). No agent leaks
  responsibility into another.
- **Orchestration is code, not magic.** The orchestrator is a
  Python service that explicitly wires the agent flow — no hidden
  LLM-driven routing in the MVP.
- **Grounding is mandatory.** Every agent uses Bing Web Search as
  a tool. Agents never fabricate facts — they search first, then
  reason over search results.
- **I/O at the edges.** FastAPI handles HTTP; agents handle AI
  reasoning; neither reaches into the other's domain.

---

## 2. Backend Architecture

### Framework Choice

| Concern | Technology | Rationale |
|---------|-----------|-----------|
| AI Agents | `agent-framework` (Microsoft Agent Framework) | Customer requirement. Provides Agent, tool, and orchestration primitives. |
| HTTP API | FastAPI | Async-native, Pydantic models, OpenAPI docs for free. Thin layer over agent orchestration. |
| LLM Provider | Azure OpenAI (`agent-framework-azure-ai`) | Azure-native, supports GPT-4o. Consistent with Azure infra. |
| Web Search | Bing Web Search API (via custom tool) | Microsoft ecosystem. Each agent gets a `search_web` tool. |
| Config | `python-dotenv` + `pydantic-settings` | Env-based config, validated at startup. No hard-coded secrets. |

### Package Layout within `src/`

```text
src/
├── agents/                     # Agent definitions (one module per agent)
│   ├── __init__.py
│   ├── general_agent.py        # General / destination-matching agent
│   ├── poi_agent.py            # Point of Interest agent
│   ├── event_agent.py          # Event / festival agent
│   ├── weather_agent.py        # Historical weather agent
│   └── tools/                  # Shared tools available to agents
│       ├── __init__.py
│       └── web_search.py       # Bing Web Search tool wrapper
├── api/                        # FastAPI application
│   ├── __init__.py
│   ├── app.py                  # FastAPI app factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── itinerary.py        # POST /api/itinerary
│   │   └── health.py           # GET /api/health
│   └── models/                 # Pydantic request/response schemas
│       ├── __init__.py
│       ├── customer.py         # CustomerProfile schema
│       └── itinerary.py        # Itinerary response schema
├── orchestrator/               # Agent orchestration logic
│   ├── __init__.py
│   └── travel_orchestrator.py  # Wires General → fan-out → fan-in
├── config/                     # App configuration
│   ├── __init__.py
│   └── settings.py             # Pydantic Settings (env vars)
└── README.md
```

### Orchestration Pattern

The orchestrator uses a **two-phase sequential-then-concurrent**
pattern:

```text
Phase 1 (Sequential):
  CustomerProfile → General Agent → List[Destination]

Phase 2 (Concurrent Fan-Out / Fan-In):
  For each Destination:
    ├── POI Agent    → List[PointOfInterest]
    ├── Event Agent  → List[Event]
    └── Weather Agent → WeatherForecast

Aggregation:
  Combine all results into a single Itinerary response
```

Implementation uses `agent-framework-orchestrations`:

```python
from agent_framework.orchestrations import ConcurrentBuilder

# Phase 2: fan-out to specialist agents
workflow = ConcurrentBuilder(
    participants=[poi_agent, event_agent, weather_agent]
).build()
results = await workflow.run(destination_context)
```

The orchestrator is a plain Python class in
`src/orchestrator/travel_orchestrator.py`. It is **not** an
agent — it is deterministic control flow that invokes agents.

---

## 3. Agent Design

### 3.1 General Agent (Destination Matcher)

| Field | Value |
|-------|-------|
| **Purpose** | Analyze customer profile and select 3–4 matching destinations |
| **Input** | `CustomerProfile` (interests, budget, travel dates, party size, departure city) |
| **Output** | `List[Destination]` — each with name, country, brief rationale |
| **System Prompt** | Located at `data/prompts/general-agent/system.md` |
| **Tools** | `search_web` — searches Bing for "best travel destinations for {interests} in {month}" |
| **Grounding Strategy** | Agent MUST call `search_web` before proposing destinations. System prompt instructs: "Search for current travel recommendations. Do not suggest destinations without search evidence." |
| **Hallucination Controls** | 1) Mandatory tool use instruction. 2) System prompt requires citing search result URLs. 3) Output schema enforced via Pydantic. |

### 3.2 POI Agent (Point of Interest)

| Field | Value |
|-------|-------|
| **Purpose** | Find top points of interest for a given destination |
| **Input** | `Destination` (name, country) + travel dates |
| **Output** | `List[PointOfInterest]` — name, description, category, estimated visit duration, source URL |
| **System Prompt** | `data/prompts/poi-agent/system.md` |
| **Tools** | `search_web` — searches "top things to do in {destination}" |
| **Grounding Strategy** | Searches travel sites (TripAdvisor, Lonely Planet patterns). Each POI must include a source URL from search results. |
| **Hallucination Controls** | 1) Must cite source for every POI. 2) Output schema validation. 3) System prompt: "Only include attractions you found in search results." |

### 3.3 Event Agent (Festivals & Events)

| Field | Value |
|-------|-------|
| **Purpose** | Find special events, festivals, and fairs at a destination during travel dates |
| **Input** | `Destination` + `travel_dates` (start, end) |
| **Output** | `List[Event]` — name, dates, description, venue, source URL |
| **System Prompt** | `data/prompts/event-agent/system.md` |
| **Tools** | `search_web` — searches "events festivals in {destination} {month} {year}" |
| **Grounding Strategy** | Time-scoped search queries ensure results match the travel window. If no events found, agent returns empty list (not fabricated events). |
| **Hallucination Controls** | 1) Date-scoped queries. 2) Must cite source. 3) System prompt: "If no events match the travel dates, return an empty list. Never invent events." |

### 3.4 Weather Agent (Historical Forecast)

| Field | Value |
|-------|-------|
| **Purpose** | Provide general weather expectations based on historical data |
| **Input** | `Destination` + `travel_dates` |
| **Output** | `WeatherForecast` — avg high/low temps, precipitation likelihood, clothing suggestions, source URL |
| **System Prompt** | `data/prompts/weather-agent/system.md` |
| **Tools** | `search_web` — searches "average weather in {destination} in {month}" |
| **Grounding Strategy** | Searches for historical averages (not real-time forecasts — those would be unreliable for future trips). |
| **Hallucination Controls** | 1) Must cite weather data source. 2) System prompt: "Base all weather information on search results for historical averages. Do not guess temperatures." |

### Shared Anti-Hallucination Pattern

All agents follow this grounding protocol:

1. **Mandatory search-first** — System prompts include:
   "You MUST call the search_web tool before answering."
2. **Cite sources** — Every factual claim must reference a URL
   from search results.
3. **Schema enforcement** — Output is parsed into Pydantic models.
   If the LLM returns malformed data, the orchestrator retries
   (max 2 retries) or returns a partial result with an error flag.
4. **Empty over fabricated** — Agents are instructed to return
   empty lists rather than inventing data.

---

## 4. API Design

### Base URL

```
/api
```

### Endpoints

#### `POST /api/itinerary`

Generate a travel itinerary from a customer profile.

**Request Body:**

```json
{
  "interests": ["history", "food", "hiking"],
  "budget": "moderate",
  "travel_dates": {
    "start": "2026-06-15",
    "end": "2026-06-25"
  },
  "party_size": 2,
  "departure_city": "Boston",
  "notes": "Prefer warm weather, no long flights"
}
```

**Response (200 OK):**

```json
{
  "destinations": [
    {
      "name": "Lisbon",
      "country": "Portugal",
      "rationale": "Rich history, world-class food scene, mild June weather",
      "points_of_interest": [
        {
          "name": "Belém Tower",
          "description": "UNESCO World Heritage Site...",
          "category": "history",
          "visit_duration_hours": 1.5,
          "source_url": "https://..."
        }
      ],
      "events": [
        {
          "name": "Festa de Santo António",
          "dates": { "start": "2026-06-12", "end": "2026-06-13" },
          "description": "Lisbon's biggest street festival...",
          "venue": "Alfama district",
          "source_url": "https://..."
        }
      ],
      "weather": {
        "avg_high_celsius": 27,
        "avg_low_celsius": 17,
        "precipitation_chance": "low",
        "clothing_suggestion": "Light layers, comfortable walking shoes",
        "source_url": "https://..."
      }
    }
  ],
  "generated_at": "2026-03-12T10:30:00Z"
}
```

**Error Responses:**

| Status | Meaning |
|--------|---------|
| 400 | Invalid input (Pydantic validation failure) |
| 500 | Agent orchestration failure |
| 503 | Upstream service unavailable (Azure OpenAI / Bing) |

#### `GET /api/health`

Health check for infrastructure probes.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Pydantic Models (shared between API and agents)

All models live in `src/api/models/` and are imported by both the
API routes and the orchestrator. This ensures a single source of
truth for the data contracts.

Key models:

- `CustomerProfile` — input to the system
- `Destination` — General Agent output
- `PointOfInterest` — POI Agent output
- `Event` — Event Agent output
- `WeatherForecast` — Weather Agent output
- `ItineraryResponse` — full aggregated response

---

## 5. Frontend Architecture

### Technology

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Framework | React 18+ with TypeScript | Customer requirement (React). TypeScript for type safety. |
| Build Tool | Vite | Fast dev server, simple config, modern defaults. |
| HTTP Client | `fetch` (native) | No extra dependency for MVP. |
| Styling | CSS Modules or Tailwind CSS | Scoped styles, no class-name collisions. |
| State Management | React `useState` / `useReducer` | MVP doesn't need Redux. Local state is sufficient. |

### Component Tree

```text
frontend/
├── src/
│   ├── App.tsx                     # Root layout + routing
│   ├── main.tsx                    # Vite entry point
│   ├── components/
│   │   ├── CustomerForm/
│   │   │   ├── CustomerForm.tsx    # Multi-field form (interests, dates, budget...)
│   │   │   └── CustomerForm.css
│   │   ├── ItineraryView/
│   │   │   ├── ItineraryView.tsx   # Renders the full itinerary
│   │   │   └── ItineraryView.css
│   │   ├── DestinationCard/
│   │   │   ├── DestinationCard.tsx # Single destination w/ POI, events, weather
│   │   │   └── DestinationCard.css
│   │   ├── LoadingState/
│   │   │   └── LoadingState.tsx    # Spinner + "Building your itinerary..."
│   │   └── ErrorState/
│   │       └── ErrorState.tsx      # Error display with retry
│   ├── api/
│   │   └── itineraryApi.ts         # fetch wrapper for POST /api/itinerary
│   ├── types/
│   │   └── itinerary.ts            # TypeScript interfaces matching API schemas
│   └── hooks/
│       └── useItinerary.ts         # Custom hook: submit profile → loading → result
├── public/
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### User Flow

```text
1. User fills out CustomerForm (interests, dates, budget, party size, departure)
2. User clicks "Build My Itinerary"
3. LoadingState shown (agent processing takes 15-30 seconds)
4. API returns → ItineraryView renders destinations
5. Each DestinationCard shows POIs, events, and weather
6. On error → ErrorState with retry button
```

### Frontend-Backend Contract

The frontend treats the API as a black box. It sends a
`CustomerProfile` and receives an `ItineraryResponse`. The
TypeScript interfaces in `types/itinerary.ts` are manually kept
in sync with the Pydantic models. (A future enhancement could
auto-generate them from the OpenAPI spec.)

---

## 6. Infrastructure

### Azure Resources

```text
┌────────────────────────────────────────────────────────────┐
│                   Azure Resource Group                      │
│                                                            │
│  ┌─────────────────────┐  ┌────────────────────────────┐   │
│  │ Azure Container App │  │ Azure Container App        │   │
│  │ (Frontend — static  │  │ (Backend — FastAPI)        │   │
│  │  SPA served by      │  │                            │   │
│  │  nginx)             │  │ Env vars:                  │   │
│  └─────────┬───────────┘  │  AZURE_OPENAI_ENDPOINT     │   │
│            │              │  AZURE_OPENAI_API_KEY       │   │
│            │ /api/*       │  BING_SEARCH_API_KEY        │   │
│            └──────────────▶  BING_SEARCH_ENDPOINT       │   │
│                           └────────────┬───────────────┘   │
│                                        │                    │
│  ┌─────────────────────┐  ┌───────────▼────────────────┐   │
│  │ Azure OpenAI        │  │ Bing Web Search            │   │
│  │ (GPT-4o deployment) │  │ (Cognitive Services)       │   │
│  └──────────┬──────────┘  └────────────────────────────┘   │
│             │                                                │
│             │ registered                                     │
│             ▼                                                │
│  ┌─────────────────────┐  ┌────────────────────────────┐   │
│  │ AI Foundry Hub      │◀─│ AI Foundry Project         │   │
│  │ (Management)        │  │ (Workspace)                │   │
│  └─────────────────────┘  └────────────────────────────┘   │
│                                                            │
│  ┌─────────────────────┐                                   │
│  │ Azure Container     │                                   │
│  │ Registry (ACR)      │                                   │
│  └─────────────────────┘                                   │
└────────────────────────────────────────────────────────────┘
```

### Bicep Modules (in `infra/`)

```text
infra/
├── main.bicep                  # Top-level orchestration
├── modules/
│   ├── container-app-env.bicep # Container Apps Environment
│   ├── container-app.bicep     # Container App (reused for FE + BE)
│   ├── acr.bicep               # Azure Container Registry
│   ├── openai.bicep            # Azure OpenAI account + deployment
│   ├── bing-search.bicep       # Bing Search resource
│   ├── ai-foundry-hub.bicep    # AI Foundry Hub for resource management
│   ├── ai-foundry-project.bicep # AI Foundry Project workspace
│   ├── ai-foundry-connection.bicep # OpenAI connection registration
│   └── keyvault.bicep          # Key Vault for secrets (optional MVP)
└── parameters/
    ├── dev.bicepparam          # Dev environment parameters
    └── prod.bicepparam         # Prod environment parameters
```

### Resource Summary

| Resource | SKU / Tier | Purpose |
|----------|-----------|---------|
| Azure Container Apps Environment | Consumption | Hosts backend + frontend containers |
| Azure Container Apps (×2) | Consumption | Backend (FastAPI) + Frontend (nginx/SPA) |
| Azure Container Registry | Basic | Store Docker images |
| Azure OpenAI | S0 | GPT-4o model deployment |
| Azure AI Foundry Hub | Standard | Centralized AI resource management and governance |
| Azure AI Foundry Project | Standard | Workspace for AI workflows and monitoring |
| Bing Web Search | S1 | Web search grounding for all agents |
| Key Vault (optional) | Standard | Secret management |

### Deployment Notes

- **MVP simplification:** Frontend could be Azure Static Web Apps
  instead of a Container App. Decision deferred to implementation.
- **No authentication in MVP.** The API is open. Auth is a
  post-MVP concern.
- **No database.** Itineraries are not persisted. The API is
  stateless.

---

## 7. Data Flow

### End-to-End Sequence

```text
┌──────────┐       ┌──────────┐       ┌───────────────┐
│  User    │       │ Frontend │       │   Backend     │
│ (Browser)│       │ (React)  │       │   (FastAPI)   │
└────┬─────┘       └────┬─────┘       └──────┬────────┘
     │                  │                     │
     │  Fill form       │                     │
     │─────────────────▶│                     │
     │                  │                     │
     │                  │  POST /api/itinerary│
     │                  │────────────────────▶│
     │                  │                     │
     │                  │              ┌──────▼──────────────────┐
     │                  │              │  Orchestrator           │
     │                  │              │                         │
     │                  │              │  1. Validate input      │
     │                  │              │  2. Call General Agent   │
     │                  │              │     ├─ search_web()     │
     │                  │              │     └─ → Destinations   │
     │                  │              │                         │
     │                  │              │  3. Fan-out (concurrent)│
     │                  │              │     ├─ POI Agent        │
     │                  │              │     │  └─ search_web()  │
     │                  │              │     ├─ Event Agent      │
     │                  │              │     │  └─ search_web()  │
     │                  │              │     └─ Weather Agent    │
     │                  │              │        └─ search_web()  │
     │                  │              │                         │
     │                  │              │  4. Fan-in: aggregate   │
     │                  │              │  5. Build Itinerary     │
     │                  │              └──────┬──────────────────┘
     │                  │                     │
     │                  │  200 OK (Itinerary) │
     │                  │◀────────────────────│
     │                  │                     │
     │  Render itinerary│                     │
     │◀─────────────────│                     │
     │                  │                     │
```

### Data Transformations

| Stage | Input | Transform | Output |
|-------|-------|-----------|--------|
| 1. Validation | Raw JSON | Pydantic parse | `CustomerProfile` |
| 2. General Agent | `CustomerProfile` | LLM + web search | `List[Destination]` (3-4 items) |
| 3a. POI Agent | `Destination` + dates | LLM + web search | `List[PointOfInterest]` per destination |
| 3b. Event Agent | `Destination` + dates | LLM + web search | `List[Event]` per destination |
| 3c. Weather Agent | `Destination` + dates | LLM + web search | `WeatherForecast` per destination |
| 4. Aggregation | All agent outputs | Deterministic merge | `ItineraryResponse` |

### Timing Expectations

- General Agent: ~5–10 seconds (1 LLM call + 1–2 search calls)
- Specialist Agents (concurrent): ~5–10 seconds each, but
  running in parallel across all destinations
- Total end-to-end: **15–30 seconds** (acceptable for MVP with
  loading indicator)

---

## 8. Testing Strategy

### Testing Pyramid

```text
         ┌───────────┐
         │   E2E     │  ← Deferred post-MVP
         │  (Playwright)
         ├───────────┤
         │Integration│  ← API routes + orchestrator with mocked agents
         ├───────────┤
         │   Unit    │  ← Agents, tools, models, orchestrator logic
         └───────────┘
```

### Test Layout

```text
tests/
├── conftest.py                 # Shared fixtures (mock LLM, mock search)
├── unit/
│   ├── agents/
│   │   ├── test_general_agent.py
│   │   ├── test_poi_agent.py
│   │   ├── test_event_agent.py
│   │   └── test_weather_agent.py
│   ├── tools/
│   │   └── test_web_search.py
│   ├── orchestrator/
│   │   └── test_travel_orchestrator.py
│   └── api/
│       └── test_models.py      # Pydantic model validation
├── integration/
│   └── test_api_routes.py      # FastAPI TestClient
└── README.md
```

### Mocking Strategy

| Component | Mock Approach |
|-----------|---------------|
| Azure OpenAI (LLM) | Mock `OpenAIChatClient` to return canned JSON responses matching agent output schemas. Each agent test provides fixture responses for its specific domain. |
| Bing Web Search | Mock `search_web` tool to return pre-recorded search results (JSON fixtures in `tests/fixtures/`). |
| Agent (in orchestrator tests) | Mock entire agent `.run()` method to return `Destination` / `PointOfInterest` / etc. objects. Tests orchestration flow, not agent internals. |
| FastAPI (in integration tests) | Use `TestClient` with dependency injection to swap real orchestrator for a mock that returns fixed itineraries. |

### Key Test Cases

**General Agent:**
- Returns 3–4 destinations for valid profile
- Calls `search_web` tool (verify tool was invoked)
- Returns valid `Destination` objects (schema compliance)
- Handles empty/minimal profile gracefully

**POI Agent:**
- Returns POIs with source URLs
- Handles unknown destinations (returns empty list, not error)

**Event Agent:**
- Date-scoped: returns only events within travel window
- Returns empty list when no events found (not fabricated events)

**Weather Agent:**
- Returns plausible temperature ranges
- Includes clothing suggestions

**Orchestrator:**
- Phase 1 → Phase 2 sequencing is correct
- Fan-out executes all three specialist agents
- Partial failure (one agent fails) returns partial itinerary
  with error flag, not a 500

**API Routes:**
- 400 on invalid input (missing required fields)
- 200 with valid itinerary structure
- Proper error response format on 500/503

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit only
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## 9. Project Structure

### Complete File Layout

```text
boston-code-camp-40/
├── Agent.md                        # Coding agent operating rules
├── Claud.md                        # LLM assistant guidance
├── README.md                       # Project overview (update with travel agent info)
├── Dockerfile                      # Backend container build
├── LICENSE
├── requirements.txt                # Python dependencies (updated)
│
├── config/                         # Environment configuration
│   ├── README.md
│   └── visualization.json
│
├── data/
│   ├── 01-raw/                     # (unused in MVP)
│   ├── 02-preprocessed/            # (unused in MVP)
│   ├── 03-features/                # (unused in MVP)
│   ├── 04-predictions/             # (unused in MVP)
│   └── prompts/                    # Runtime agent prompts
│       ├── README.md
│       ├── general-agent/
│       │   └── system.md           # General Agent system prompt
│       ├── poi-agent/
│       │   └── system.md           # POI Agent system prompt
│       ├── event-agent/
│       │   └── system.md           # Event Agent system prompt
│       └── weather-agent/
│           └── system.md           # Weather Agent system prompt
│
├── docs/
│   └── architecture.md             # This document
│
├── entrypoints/
│   ├── README.md
│   └── serve.py                    # Uvicorn entry point for FastAPI
│
├── frontend/                       # React application (NEW)
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── CustomerForm/
│   │   │   ├── ItineraryView/
│   │   │   ├── DestinationCard/
│   │   │   ├── LoadingState/
│   │   │   └── ErrorState/
│   │   ├── api/
│   │   │   └── itineraryApi.ts
│   │   ├── types/
│   │   │   └── itinerary.ts
│   │   └── hooks/
│   │       └── useItinerary.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── infra/                          # Azure Bicep IaC
│   ├── README.md
│   ├── main.bicep
│   ├── modules/
│   │   ├── container-app-env.bicep
│   │   ├── container-app.bicep
│   │   ├── acr.bicep
│   │   ├── openai.bicep
│   │   ├── bing-search.bicep
│   │   └── keyvault.bicep
│   └── parameters/
│       ├── dev.bicepparam
│       └── prod.bicepparam
│
├── notebooks/                      # EDA / prototyping
│   └── README.md
│
├── reports/                        # Generated reports
│   └── README.md
│
├── src/
│   ├── README.md
│   ├── agents/                     # Agent definitions
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── general_agent.py
│   │   ├── poi_agent.py
│   │   ├── event_agent.py
│   │   ├── weather_agent.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       └── web_search.py
│   ├── api/                        # FastAPI application (NEW)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── itinerary.py
│   │   │   └── health.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── customer.py
│   │       └── itinerary.py
│   ├── orchestrator/               # Orchestration logic (NEW)
│   │   ├── __init__.py
│   │   └── travel_orchestrator.py
│   ├── config/                     # App settings (NEW)
│   │   ├── __init__.py
│   │   └── settings.py
│   └── pipelines/
│       └── README.md
│
└── tests/
    ├── README.md
    ├── conftest.py
    ├── fixtures/                    # Canned JSON responses (NEW)
    │   ├── search_results/
    │   └── agent_responses/
    ├── unit/
    │   ├── agents/
    │   │   ├── test_general_agent.py
    │   │   ├── test_poi_agent.py
    │   │   ├── test_event_agent.py
    │   │   └── test_weather_agent.py
    │   ├── tools/
    │   │   └── test_web_search.py
    │   ├── orchestrator/
    │   │   └── test_travel_orchestrator.py
    │   └── api/
    │       └── test_models.py
    └── integration/
        └── test_api_routes.py
```

### New Dependencies (additions to `requirements.txt`)

```text
# Microsoft Agent Framework
agent-framework
agent-framework-azure-ai
agent-framework-orchestrations

# Web API
fastapi
uvicorn[standard]

# Configuration
python-dotenv
pydantic-settings

# HTTP client (for Bing Search tool)
httpx
```

---

## 10. Implementation Priority

### Phase 1 — Foundation (Build First)

> Goal: Runnable backend that returns a hardcoded itinerary.

| # | Task | Owner | Depends On |
|---|------|-------|------------|
| 1.1 | Pydantic models (`src/api/models/`) | Backend | — |
| 1.2 | App settings / config (`src/config/settings.py`) | Backend | — |
| 1.3 | FastAPI app + health endpoint | Backend | 1.1 |
| 1.4 | `POST /api/itinerary` route (stub: returns mock data) | Backend | 1.1, 1.3 |
| 1.5 | `entrypoints/serve.py` (Uvicorn runner) | Backend | 1.3 |
| 1.6 | Unit tests for Pydantic models | Test | 1.1 |

### Phase 2 — Agents (Build Second)

> Goal: Working agents that call Azure OpenAI + Bing Search.

| # | Task | Owner | Depends On |
|---|------|-------|------------|
| 2.1 | Bing Search tool (`src/agents/tools/web_search.py`) | Backend | 1.2 |
| 2.2 | Agent system prompts (`data/prompts/*/system.md`) | Backend | — |
| 2.3 | General Agent implementation | Backend | 2.1, 2.2 |
| 2.4 | POI Agent implementation | Backend | 2.1, 2.2 |
| 2.5 | Event Agent implementation | Backend | 2.1, 2.2 |
| 2.6 | Weather Agent implementation | Backend | 2.1, 2.2 |
| 2.7 | Unit tests for all agents (mocked LLM + search) | Test | 2.3–2.6 |

### Phase 3 — Orchestration (Build Third)

> Goal: End-to-end flow from customer input to itinerary.

| # | Task | Owner | Depends On |
|---|------|-------|------------|
| 3.1 | Travel Orchestrator (`src/orchestrator/`) | Backend | 2.3–2.6 |
| 3.2 | Wire orchestrator into `POST /api/itinerary` route | Backend | 3.1, 1.4 |
| 3.3 | Orchestrator unit tests | Test | 3.1 |
| 3.4 | Integration tests (API → Orchestrator → mock agents) | Test | 3.2 |

### Phase 4 — Frontend (Build Fourth) ✅ **COMPLETE**

> Goal: React UI that calls the real backend.
>
> **Status:** ✅ All 5 components built, useItinerary hook complete, API client tested. 66 tests passing. Build: 204 KB JS (64 KB gzipped), 7.8 KB CSS.

| # | Task | Owner | Depends On |
|---|------|-------|------------|
| 4.1 | Vite + React + TypeScript scaffold | Frontend | — |
| 4.2 | TypeScript type definitions (match Pydantic models) | Frontend | 1.1 |
| 4.3 | API client (`itineraryApi.ts`) | Frontend | 4.1, 1.4 |
| 4.4 | CustomerForm component | Frontend | 4.1 |
| 4.5 | ItineraryView + DestinationCard components | Frontend | 4.2 |
| 4.6 | Loading + Error states | Frontend | 4.1 |
| 4.7 | Wire it all together in App.tsx | Frontend | 4.3–4.6 |

### Phase 5 — Infrastructure (Build Fifth) ✅ **COMPLETE**

> Goal: Deployable to Azure via Bicep.
>
> **Status:** ✅ Backend Dockerfile (Python 3.12-slim, 4 Uvicorn workers). Frontend Dockerfile (multi-stage node+nginx). 5 Bicep modules (container-app-env, container-app, acr, openai, bing-search). main.bicep orchestrating 6 Azure resources. Dev/prod parameter files. 74 infra validation tests (+ 4 Docker skipped without Docker).

| # | Task | Owner | Status |
|---|------|-------|--------|
| 5.1 | Dockerfile for backend | Infra | ✅ Done |
| 5.2 | Bicep modules (ACR, Container Apps, OpenAI, Bing) | Infra | ✅ Done |
| 5.3 | `main.bicep` orchestration | Infra | ✅ Done |
| 5.4 | Parameter files (dev, prod) | Infra | ✅ Done |

### Phase 6 — Polish (Build Last) ✅ **COMPLETE**

> Goal: Error handling hardening, loading UX polish, comprehensive error testing.
>
> **Status:** ✅ COMPLETE — Phase 6.1 backend error hardening with structured JSON responses, graceful degradation, timeout handling (Batty). Phase 6.2 loading UX polish with multi-step progress indicator, CSS animations, skeleton loaders, accessible error states (Pris). Phase 6.3 comprehensive error handling test coverage for API, orchestrator, agents, web search (Zhora). 262 backend tests passing, 63 frontend tests passing, zero failures.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 6.1 | Error handling hardening (structured responses, graceful degradation, timeouts) | Backend | ✅ Done |
| 6.2 | Loading UX polish (progress indicators, CSS animations, skeleton loaders, error states) | Frontend | ✅ Done |
| 6.3 | Error handling test coverage (API errors, orchestrator degradation, agent failures, web search) | Test | ✅ Done |

---

## Appendix: Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| API framework | FastAPI | Flask, aiohttp | Async-native, Pydantic integration, auto-generated OpenAPI docs. Best fit for an agent backend that's I/O-bound. |
| Agent framework | Microsoft Agent Framework (`agent-framework`) | Semantic Kernel, LangChain | Explicit customer requirement. NOT Semantic Kernel. |
| Orchestration pattern | Sequential → ConcurrentBuilder fan-out | Full LLM-driven routing, sequential-only | Fan-out gives parallelism (faster). Sequential General → Specialist ensures destinations are decided before details are gathered. Deterministic orchestrator (not LLM) keeps flow predictable. |
| Web search grounding | Bing Web Search API | Tavily, SerpAPI, Google Search | Microsoft ecosystem consistency. Available as Azure Cognitive Service. |
| Frontend framework | React + Vite + TypeScript | Next.js, plain React | Customer requires React. Vite is the modern standard for SPA builds. TypeScript for contract safety. No SSR needed (pure SPA). |
| Prompt storage | `data/prompts/` (Markdown files) | Inline strings, database | Follows existing repo convention (Agent.md, Claud.md). Version-controlled. Easy to review in PRs. |
| No database | Stateless API | PostgreSQL, CosmosDB | MVP scope explicitly excludes itinerary persistence. Adding state adds complexity for no MVP benefit. |
| No auth | Open API | Azure AD, API keys | MVP scope explicitly excludes authentication. Will be needed post-MVP. |

---

*This document is the single source of truth for the travel agent
application architecture. All implementation should follow these
patterns. Deviations require an architecture decision record in
`.squad/decisions/inbox/`.*
