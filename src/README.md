# `src/` — Backend Production Code

This folder contains all backend production code for the Travel Agent Application. For the frontend (React + TypeScript), see [frontend/README.md](../frontend/README.md).

## Organization

```
src/
├── agents/                 # AI agent implementations
│   ├── general_agent.py    # Destination matching agent
│   ├── poi_agent.py        # Points of interest agent
│   ├── event_agent.py      # Events/festivals agent
│   ├── weather_agent.py    # Historical weather agent
│   └── tools/              # Shared tools (web_search.py)
├── api/                    # FastAPI application
│   ├── app.py              # App factory and configuration
│   ├── routes/             # API endpoints
│   │   ├── itinerary.py    # POST /api/itinerary
│   │   └── health.py       # GET /api/health
│   └── models/             # Pydantic request/response schemas
│       ├── customer.py     # CustomerProfile input schema
│       └── itinerary.py    # Itinerary response schema
├── orchestrator/           # Orchestration service
│   └── travel_orchestrator.py  # Two-phase orchestration (General → fan-out POI/Event/Weather)
├── config/                 # Application configuration
│   └── settings.py         # Pydantic Settings (environment variables)
└── pipelines/              # Reusable pipeline code (unused in MVP, preserved from template)
```

## Key Modules

### agents/
Contains the four AI agents that reason over web search results:
- Each agent has a defined system prompt (stored in `data/prompts/{agent-name}/system.md`)
- Each agent uses the `search_web` tool from `agents/tools/web_search.py`
- See [agents/README.md](agents/README.md) for details

### api/
FastAPI application that exposes two endpoints:
- `POST /api/itinerary` — Accept customer profile, return itinerary
- `GET /api/health` — Liveness check

Request/response models are validated with Pydantic schemas.

### orchestrator/
Implements the **two-phase orchestration pattern**:
1. **Phase 1 (Sequential):** Call General Agent with customer profile → get destinations
2. **Phase 2 (Concurrent):** For each destination, fan-out to POI / Event / Weather agents in parallel
3. **Aggregation:** Collect all results and return aggregated itinerary

### config/
Application settings (API keys, endpoints, etc.) loaded from environment variables via Pydantic Settings. Never hard-code secrets.

### pipelines/
**Preserved from template but unused in MVP.** Will be useful for future feature engineering or batch processing workflows.

## Development Guidelines

- Agent logic lives here; agent prompts live in `data/prompts/`
- Entry points (`entrypoints/serve.py`) should be thin: parse args, call orchestrator
- All API response models are Pydantic schemas in `src/api/models/`
- Tests live in `tests/`; mirrors `src/` structure

## See Also

- [docs/architecture.md](../docs/architecture.md) — System design and agent flow
- [agents/README.md](agents/README.md) — Agent design and tools
- [tests/README.md](../tests/README.md) — Testing strategy
