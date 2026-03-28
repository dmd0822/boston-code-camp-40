# Travel Agent Application

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build, Test & Deploy](https://github.com/dmd0822/boston-code-camp-40/actions/workflows/deploy-app-dev.yml/badge.svg)](https://github.com/dmd0822/boston-code-camp-40/actions/workflows/deploy-app-dev.yml)
![Backend Tests](https://img.shields.io/badge/backend_tests-5_failing-red)
![Frontend Tests](https://img.shields.io/badge/frontend_tests-0_passing-brightgreen)
![Total Tests](https://img.shields.io/badge/total_tests-failing-red)

> **Build personalized travel itineraries using multiple AI agents grounded in web search.**

A FastAPI backend orchestrates five specialized travel agents (General,
POI, Event, Weather, Travel Advisory) to build grounded itineraries end-to-end. The app
uses Microsoft Agent Framework with Azure AI Foundry Agent Service,
authenticates through `DefaultAzureCredential`, ships with a React
frontend in `src/frontend/`, and deploys to Azure Container Apps with
Bicep and GitHub Actions.

**Status:** ✅ **All Phases Complete** — The application works end-to-end
locally and in Azure, with managed identity authentication, CI/CD, and a
current validation snapshot of 242 passing tests and 4 skipped Docker
checks.

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Agents** | Microsoft Agent Framework (`agent-framework`, `agent-framework-azure-ai`) | Define agent behavior, tools, and orchestration |
| **Agent Runtime** | Azure AI Foundry Agent Service (`AzureAIClient`) | Server-side agent execution against the project endpoint |
| **Authentication** | Azure Identity `DefaultAzureCredential` | `az login` locally, managed identity in Azure Container Apps |
| **Web Grounding** | Bing Web Search API | Search-first grounding pattern for itinerary recommendations |
| **HTTP API** | FastAPI + Uvicorn | Async REST backend |
| **Config** | Pydantic Settings + `python-dotenv` | Environment-based configuration without hard-coded secrets |
| **Frontend** | React 19 + Vite + TypeScript | SPA with customer form, itinerary view, hooks, and API client |
| **Containers** | Docker + nginx | Backend Python container plus frontend multi-stage Node/nginx image |
| **Infrastructure** | Azure Bicep | `main.bicep` plus 7 reusable modules for ACR, Container Apps, AI Foundry, Bing, and RBAC |
| **CI/CD** | GitHub Actions + Azure OIDC | Build, test, badge update, image push, infra deploy, and app deploy |
| **Testing** | pytest + Vitest | Backend, infrastructure, and frontend validation |
| **Language** | Python 3.12 + TypeScript | Backend and frontend runtimes |

## System Architecture

```
┌────────────────────────────────────────┐
│     React Frontend (Vite + nginx)      │
│ User form → submit profile → view trip │
└──────────────────┬─────────────────────┘
                   │ HTTPS /api/*
                   ▼
┌────────────────────────────────────────┐
│     FastAPI Backend (Python)           │
│                                        │
│ POST /api/itinerary                    │
│ ├─ General Agent                       │
│ ├─ POI Agent                           │
│ ├─ Event Agent                         │
│ ├─ Weather Agent                       │
│ ├─ Travel Advisory Agent               │
│ └─ Travel Orchestrator                 │
│                                        │
│ GET /api/health                        │
└──────────────┬───────────────┬─────────┘
               │               │
               ▼               ▼
┌──────────────────────┐  ┌──────────────────────┐
│ Azure AI Foundry     │  │ Bing Web Search API  │
│ Agent Service        │  │ Grounding source     │
│ GPT-4o deployment    │  │ for agent research   │
└──────────────────────┘  └──────────────────────┘
```

**Key Principles:**
- **Explicit boundaries:** Each agent has a defined role, prompt, and
  output contract.
- **Grounding mandatory:** Agents search first and reason over grounded
  results.
- **Orchestration as code:** Deterministic Python coordinates the full
  itinerary flow.
- **Managed identity first:** Local development uses Azure CLI auth;
  deployed apps use managed identities.

## Getting Started

### Prerequisites

- Python 3.10+ for the backend
- Node.js 18+ and npm for the frontend
- Azure CLI with access to your Azure subscription
- Git

### Quick Start

#### 1. Clone the repository and set up the backend

```bash
git clone <repo-url>
cd boston-code-camp-40

python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

#### 2. Authenticate and configure the environment

```bash
az login
cp .env.template .env
```

Edit `.env` with the current runtime variables:

```
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
APP_VERSION=0.1.0
```

No Azure AI or Bing API keys are required. Locally,
`DefaultAzureCredential` uses your Azure CLI session. In Azure, the
backend uses the Container App's system-assigned managed identity.

#### 3. Start the backend server

```bash
python entrypoints/serve.py
```

Backend runs on `http://localhost:8000`.

#### 4. Set up and run the frontend

```bash
cd src/frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and proxies `/api/*` to the
backend during development.

#### 5. Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Build an itinerary
curl -X POST http://localhost:8000/api/itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "interests": ["hiking", "museums"],
    "budget": "moderate",
    "trip_duration": 7,
    "travel_style": "adventurous"
  }'
```

## Project Structure

```
boston-code-camp-40/
├── README.md                     # This file
├── LICENSE                       # MIT License
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Backend container image
├── .env.template                 # Local environment template
├── pytest.ini                    # Pytest configuration
├── .github/
│   └── workflows/
│       ├── deploy-app-dev.yml    # Build, test, badge update, image push, deploy
│       └── deploy-infra-dev.yml  # Validate and deploy Azure infrastructure
│
├── src/
│   ├── agents/                   # AI agent implementations and tools
│   ├── api/                      # FastAPI application and models
│   ├── config/                   # Settings and environment loading
│   ├── frontend/                 # React + TypeScript frontend
│   │   ├── src/                  # Components, hooks, API client, types
│   │   ├── Dockerfile            # Frontend container image
│   │   ├── entrypoint.sh         # envsubst startup for nginx config
│   │   ├── nginx.conf.template   # Runtime proxy template
│   │   ├── package.json          # Frontend scripts and deps
│   │   └── README.md             # Frontend setup and architecture
│   ├── orchestrator/             # Travel orchestration flow
│   ├── pipelines/                # Template-preserved reusable code
│   └── README.md                 # Backend folder overview
│
├── entrypoints/                  # Runnable scripts
│   ├── serve.py                  # Start the backend server
│   └── README.md
│
├── tests/                        # Automated tests
│   ├── unit/                     # Backend unit tests
│   ├── integration/              # Backend integration tests
│   ├── infra/                    # Infrastructure validation tests
│   ├── fixtures/                 # Shared fixtures and mock data
│   └── README.md
│
├── infra/                        # Azure infrastructure as code
│   ├── main.bicep                # Orchestrates shared Azure resources
│   ├── modules/                  # 7 reusable Bicep modules
│   │   ├── acr.bicep
│   │   ├── acr-role-assignment.bicep
│   │   ├── ai-foundry.bicep
│   │   ├── bing-search.bicep
│   │   ├── container-app-env.bicep
│   │   ├── container-app.bicep
│   │   └── role-assignment.bicep
│   ├── parameters/
│   │   ├── dev.bicepparam
│   │   └── prod.bicepparam
│   ├── environments.json         # Environment naming and location config
│   └── README.md                 # Deployment guide and module reference
│
├── config/                       # Configuration documentation
├── data/                         # Prompts and data artifacts
├── docs/                         # Architecture and diagrams
├── notebooks/                    # Exploration notebooks
└── reports/                      # Generated outputs
```

**Key folders documented separately:**
- [src/frontend/README.md](src/frontend/README.md) — Frontend setup,
  components, testing, and deployment runtime
- [src/README.md](src/README.md) — Backend code organization
- [src/agents/README.md](src/agents/README.md) — AI agents and tools
- [src/pipelines/README.md](src/pipelines/README.md) — Reusable pipeline
  code preserved from the template
- [entrypoints/README.md](entrypoints/README.md) — Entry points and
  server startup
- [tests/README.md](tests/README.md) — Testing strategy and coverage
- [config/README.md](config/README.md) — Configuration management
- [data/README.md](data/README.md) — Data staging and prompt artifacts
- [data/prompts/README.md](data/prompts/README.md) — Agent system prompts
- [infra/README.md](infra/README.md) — Azure infrastructure templates

## API Endpoints

### `POST /api/itinerary`

Build a personalized travel itinerary.

**Request:**
```json
{
  "name": "Alice",
  "interests": ["hiking", "museums", "local cuisine"],
  "budget": "moderate",
  "trip_duration": 7,
  "travel_style": "adventurous"
}
```

**Response:**
```json
{
  "destinations": [
    {
      "name": "Banff, Canada",
      "country": "Canada",
      "rationale": "...",
      "points_of_interest": [],
      "events": [],
      "weather": {
        "avg_high_celsius": 22,
        "avg_low_celsius": 8,
        "precipitation_chance": "moderate",
        "clothing_suggestion": "Layers for mountain weather",
        "source_url": "https://..."
      },
      "travel_advisory": {
        "advisory_level": 1,
        "advisory_summary": "Exercise normal precautions in Canada",
        "specific_warnings": ["Standard travel safety measures apply"],
        "last_updated": "2026-03-01",
        "source_url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/canada-travel-advisory.html"
      }
    }
  ],
  "generated_at": "2026-03-12T10:30:00Z"
}
```

### `GET /api/health`

Liveness check.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

## Running Tests

### Backend Tests (123 passing)

```bash
# Run backend unit + integration tests
pytest tests/unit tests/integration

# Run with coverage
pytest tests/unit tests/integration --cov=src --cov-report=html

# Run a specific backend test file
pytest tests/unit/agents/test_general_agent.py

# Verbose output
pytest tests/unit tests/integration -v
```

### Infrastructure Tests (109 passing, 4 Docker build checks skipped without Docker daemon)

```bash
# Run all infrastructure validation tests
pytest tests/infra/

# Skip Docker build validation checks
pytest tests/infra/ -m "not docker_build"
```

### Frontend Tests (66 passing)

```bash
cd src/frontend

# Run all frontend tests
npm run test

# Run with coverage
npm run test -- --coverage

# Watch mode
npm run test:watch
```

**Current validation snapshot:** 242 passing, 4 skipped.

See [tests/README.md](tests/README.md) for detailed coverage notes.

## Infrastructure ✅

The application is fully containerized and deploys to Azure Container
Apps with Bicep and managed identities.

### Infrastructure modules (7 total)

- `acr.bicep` — Azure Container Registry with `adminUserEnabled: false`
- `container-app-env.bicep` — Shared Container Apps environment
- `container-app.bicep` — Reusable container app module with
  system-assigned + user-assigned identity support and registry pulls via
  identity instead of passwords
- `ai-foundry.bicep` — Combined AI Services account, AI Foundry project,
  and GPT-4o deployment
- `bing-search.bicep` — Bing Search resource module for search-backed
  scenarios
- `role-assignment.bicep` — Resource-group-scoped RBAC assignments with
  deterministic GUIDs and an `enabled` switch
- `acr-role-assignment.bicep` — ACR-scoped RBAC assignments for image
  pull permissions

### Deployment notes

- Parameter files live in `infra/parameters/dev.bicepparam` and
  `infra/parameters/prod.bicepparam`
- Backend runtime configuration uses only:
  `AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`, and
  `APP_VERSION`
- Backend authentication uses `DefaultAzureCredential`
  (`az login` locally, system-assigned managed identity in Azure)
- The backend managed identity receives the **Azure AI User** role at
  resource-group scope so it can call Azure AI Foundry Agent Service
- Frontend container startup uses `src/frontend/nginx.conf.template` and
  `src/frontend/entrypoint.sh` to inject `BACKEND_URL` and `BACKEND_HOST`
  via `envsubst`, with `proxy_ssl_server_name on` for TLS proxying

For deployment details, see [infra/README.md](infra/README.md).

## CI/CD

Two GitHub Actions workflows keep the dev environment current:

- **`deploy-infra-dev.yml`** — Deploy Infrastructure
  - Triggers on `infra/**` changes or manual dispatch
  - Loads environment config, validates Bicep, runs What-If, and deploys
    to Azure
- **`deploy-app-dev.yml`** — Build, Test & Deploy
  - Triggers on `src/**` changes, successful infra workflow completion,
    or manual dispatch
  - Runs 5 jobs: `load-config` → `test-backend` + `test-frontend`
    (parallel) → `update-readme` → `build` → `deploy`
  - Builds backend and frontend images, pushes to ACR, updates Container
    Apps, and refreshes README badge counts

Both workflows use Azure OIDC / federated credentials for deployment,
not long-lived deployment secrets.

## Development

### Code Style

Python code follows:
- PEP 8 formatting
- Type hints via the `typing` module
- PEP 257 docstrings for public functions and classes
- Clear, composable functions with intent-driven names

### Architecture Decisions

All significant architectural decisions are documented in:
- **[docs/architecture.md](docs/architecture.md)** — Single source of
  truth for system design
- **[docs/diagrams.md](docs/diagrams.md)** — Visual architecture diagrams
- **[.squad/decisions.md](.squad/decisions.md)** — Team decisions and
  approvals

Read `docs/architecture.md` before making changes that affect agent
flow, API contracts, authentication, or deployment patterns.

### Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run the relevant local validation
4. Push and open a pull request
5. Ensure CI passes before merging

## License

MIT License. See [LICENSE](LICENSE).
