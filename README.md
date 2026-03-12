# Travel Agent Application

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Build personalized travel itineraries using multiple AI agents grounded in web search.**

A FastAPI backend application that orchestrates four specialized AI agents (General, POI, Event, Weather) to create comprehensive travel itineraries. Each agent is grounded in Bing Web Search to ensure factual accuracy. The application is built with Microsoft Agent Framework and deployed on Azure Container Apps.

**Phase 1 Status:** ✅ Backend & tests complete. APIs ready. Foundation ready for frontend and infrastructure deployment.

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Agents** | Microsoft Agent Framework (`agent-framework`) | Define agents, tools, and reasoning |
| **LLM** | Azure OpenAI (GPT-4o) | Reasoning engine for agents |
| **Web Grounding** | Bing Web Search API | Mandatory search-first pattern for all agents |
| **HTTP API** | FastAPI + Uvicorn | Async REST backend |
| **Config** | Pydantic Settings + `python-dotenv` | Environment-based config (no hard-coded secrets) |
| **Testing** | pytest | Unit & integration tests |
| **Frontend** | React + Vite + TypeScript | SPA consuming the `/api/itinerary` endpoint |
| **Infrastructure** | Azure Bicep | IaC for Container Apps, registries, OpenAI, and search APIs |
| **Language** | Python 3.x | Backend runtime |

## System Architecture

```
┌────────────────────────────────────────┐
│      React Frontend (Vite + TS)        │
│  User form → customer profile submit   │
└──────────────────┬─────────────────────┘
                   │ HTTPS POST
                   ▼
┌────────────────────────────────────────┐
│    FastAPI Backend (Python)            │
│                                        │
│  POST /api/itinerary                   │
│  ├─ Orchestrator Service               │
│  │  ├─ Phase 1: General Agent          │
│  │  │  (destination matching)          │
│  │  └─ Phase 2: Concurrent fan-out     │
│  │     ├─ POI Agent                    │
│  │     ├─ Event Agent                  │
│  │     └─ Weather Agent                │
│  └─ Return aggregated itinerary        │
│                                        │
│  GET /api/health                       │
│  └─ Liveness check                     │
└──────────────────┬─────────────────────┘
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
┌──────────────────┐  ┌──────────────────┐
│ Azure OpenAI     │  │ Bing Web Search  │
│ (GPT-4o)         │  │ (grounding tool) │
└──────────────────┘  └──────────────────┘
```

**Key Principles:**
- **Explicit boundaries:** Each agent has defined inputs/outputs and a system prompt.
- **Grounding mandatory:** All agents search first, then reason over results (no hallucination).
- **Orchestration as code:** Deterministic Python flow, not LLM-driven routing.
- **Async-native:** FastAPI handles concurrent agent calls efficiently.

## Getting Started

### Prerequisites

- Python 3.10 or later
- An Azure subscription (Azure OpenAI, Bing Web Search)
- Git

### Quick Start

#### 1. Clone and setup Python environment

```bash
git clone <repo-url>
cd boston-code-camp-40

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure environment

```bash
# Copy template and fill in your Azure credentials
cp .env.template .env
```

Edit `.env` with:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
BING_SEARCH_API_KEY=your-bing-key
BING_SEARCH_ENDPOINT=https://api.bing.microsoft.com/
APP_VERSION=0.1.0
```

#### 3. Run the server

```bash
python entrypoints/serve.py
```

Server starts on `http://localhost:8000`

#### 4. Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Build an itinerary (example)
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
├── README.md                  # This file
├── LICENSE                    # MIT License
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container build for backend
├── .env.template              # Environment variables template
│
├── src/                       # Production code
│   ├── agents/                # AI agent implementations (4 agents: General, POI, Event, Weather)
│   │   ├── general_agent.py   # Destination matching agent
│   │   ├── poi_agent.py       # Points of interest agent
│   │   ├── event_agent.py     # Events/festivals agent
│   │   ├── weather_agent.py   # Historical weather agent
│   │   └── tools/             # Shared tools (e.g., web_search.py)
│   ├── api/                   # FastAPI application
│   │   ├── app.py             # App factory
│   │   ├── routes/            # API endpoints (/itinerary, /health)
│   │   └── models/            # Pydantic schemas (CustomerProfile, Itinerary)
│   ├── orchestrator/          # Orchestration logic (two-phase flow)
│   │   └── travel_orchestrator.py
│   ├── config/                # App configuration (Pydantic Settings)
│   │   └── settings.py
│   └── README.md              # src/ documentation
│
├── entrypoints/               # Runnable scripts
│   ├── serve.py               # Start the FastAPI server on port 8000
│   └── README.md
│
├── tests/                     # Automated tests (pytest)
│   ├── unit/                  # Unit tests for agents, API models
│   ├── integration/           # Integration tests for orchestrator
│   ├── fixtures/              # Test fixtures and mock data
│   ├── conftest.py            # Pytest configuration
│   └── README.md
│
├── config/                    # Configuration files
│   └── README.md
│
├── data/                      # Data & artifacts
│   ├── prompts/               # Agent system prompts (Markdown)
│   │   ├── general/system.md
│   │   ├── poi/system.md
│   │   ├── event/system.md
│   │   └── weather/system.md
│   ├── 01-raw/                # Raw input data (unused in MVP)
│   ├── 02-preprocessed/       # Preprocessed data (unused in MVP)
│   ├── 03-features/           # Feature data (unused in MVP)
│   └── 04-predictions/        # Predictions (unused in MVP)
│
├── infra/                     # Infrastructure as Code (Bicep)
│   ├── main.bicep             # Main deployment template
│   └── modules/               # Modular Bicep templates (Container Apps, registries, etc.)
│
├── notebooks/                 # EDA & exploration (not production code)
└── reports/                   # Generated reports and outputs
```

**Key folders documented separately:**
- [src/README.md](src/README.md) — Backend code organization
- [src/agents/README.md](src/agents/README.md) — AI agents and tools
- [src/pipelines/README.md](src/pipelines/README.md) — Reusable pipeline code (note: currently unused in MVP)
- [entrypoints/README.md](entrypoints/README.md) — Entry points and server startup
- [tests/README.md](tests/README.md) — Testing strategy and structure
- [config/README.md](config/README.md) — Configuration management
- [data/README.md](data/README.md) — Data staging and prompt artifacts
- [data/prompts/README.md](data/prompts/README.md) — Agent system prompts
- [infra/README.md](infra/README.md) — Infrastructure templates (Bicep)

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
  "itinerary_id": "uuid",
  "destinations": [
    {
      "destination": "Banff, Canada",
      "description": "...",
      "source_url": "...",
      "pois": [...],
      "events": [...],
      "weather_forecast": {...}
    }
  ]
}
```

### `GET /api/health`

Liveness check.

**Response:** `{"status": "ok"}`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_general_agent.py

# Run with verbose output
pytest -v
```

See [tests/README.md](tests/README.md) for test structure and coverage details.


## Development

### Code Style

Python code follows:
- PEP 8 formatting
- Type hints via 	yping module
- PEP 257 docstrings for public functions/classes
- Clear, composable functions with intent-driven names

### Architecture Decisions

All significant architectural decisions are documented in:
- **[docs/architecture.md](docs/architecture.md)** — Single source of truth for system design
- **[.squad/decisions.md](.squad/decisions.md)** — Team decisions and approvals

**For developers:** Read docs/architecture.md before making changes that affect agent flow, API contracts, or deployment patterns.

### Contributing

1. Create a feature branch: git checkout -b feature/your-feature
2. Make changes and add tests
3. Run tests locally: pytest
4. Push and open a pull request
5. All PRs must pass CI and code review

## License

MIT License. See [LICENSE](LICENSE).
