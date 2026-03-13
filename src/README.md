# `src/` — Backend Production Code

This folder contains all backend production code for the Travel Agent
Application. For the frontend (React + TypeScript), see
[frontend/README.md](frontend/README.md).

## Organization

```
src/
├── agents/                 # AI agent implementations
│   ├── general_agent.py    # Destination matching agent
│   ├── poi_agent.py        # Points of interest agent
│   ├── event_agent.py      # Events and festivals agent
│   ├── weather_agent.py    # Weather forecast agent
│   └── tools/              # Shared tools (web_search.py)
├── api/                    # FastAPI application
│   ├── app.py              # App factory and configuration
│   ├── routes/             # API endpoints
│   │   ├── itinerary.py    # POST /api/itinerary
│   │   └── health.py       # GET /api/health
│   └── models/             # Pydantic request/response schemas
├── config/                 # Application configuration
│   └── settings.py         # Pydantic Settings + env var loading
├── frontend/               # React + TypeScript SPA
├── orchestrator/           # Orchestration service
│   └── travel_orchestrator.py  # General → fan-out flow
└── pipelines/              # Reusable pipeline code (unused in MVP)
```

## Key Modules

### agents/
Contains the four AI agents that reason over grounded results:
- Each agent has a system prompt in `data/prompts/{agent-name}/system.md`
- Each agent uses the shared web search tool in `agents/tools/`
- See [agents/README.md](agents/README.md) for details

### api/
FastAPI exposes two endpoints:
- `POST /api/itinerary` — Accept customer profile and return itinerary
- `GET /api/health` — Liveness check with app version

### orchestrator/
Implements the two-phase orchestration pattern:
1. **Phase 1:** General Agent recommends destinations
2. **Phase 2:** POI / Event / Weather agents run concurrently per
   destination
3. **Aggregation:** Results are combined into the itinerary response

### config/
Application settings are loaded from environment variables via Pydantic
Settings. The backend uses `AZURE_AI_PROJECT_ENDPOINT`,
`AZURE_AI_MODEL_DEPLOYMENT_NAME`, and `APP_VERSION`, while
`DefaultAzureCredential` handles authentication through Azure CLI locally
and managed identity in Azure.

### frontend/
The React frontend now lives under `src/frontend/`, keeping the UI,
Docker runtime, and backend source tree in one place.

### pipelines/
Preserved from the template and currently unused in the MVP.

## Development Guidelines

- Agent logic lives here; prompts live in `data/prompts/`
- Entry points (`entrypoints/serve.py`) stay thin and delegate to the
  backend modules in `src/`
- API contracts are defined in `src/api/models/`
- Tests live in `tests/` and `src/frontend/`, mirroring the app layers

## See Also

- [docs/architecture.md](../docs/architecture.md) — System design and
  agent flow
- [agents/README.md](agents/README.md) — Agent design and tools
- [frontend/README.md](frontend/README.md) — Frontend implementation
- [tests/README.md](../tests/README.md) — Testing strategy
