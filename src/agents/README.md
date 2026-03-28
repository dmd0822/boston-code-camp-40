# src/agents/ — AI Agents

This folder contains the five specialized AI agents that power the
Travel Agent Application, implemented with Microsoft Agent Framework and
Azure AI Foundry Agent Service.

## Agents

1. **General Agent** — Destination matching and selection
2. **POI Agent** — Points of interest discovery
3. **Event Agent** — Events, festivals, and cultural attractions
4. **Weather Agent** — Weather and seasonal planning guidance
5. **Travel Advisory Agent** — U.S. State Department travel advisory lookup

## Agent Design Principles

- **Explicit boundaries:** Each agent has a clearly defined role,
  inputs, and outputs
- **Grounding mandatory:** Agents use web search as part of the
  search-first reasoning pattern
- **System prompts:** Each agent loads instructions from
  `data/prompts/{agent-name}/system.md`
- **Server-side execution:** Agent runs are hosted through Azure AI
  Foundry Agent Service via `AzureAIClient`
- **Managed identity auth:** Authentication flows through
  `DefaultAzureCredential`
- **Type-safe:** Outputs are validated with Pydantic models
- **Graceful errors:** Missing configuration or malformed responses
  return empty results rather than crashing the API

## Folder Structure

```
src/agents/
├── __init__.py              # Public exports for all agents
├── general_agent.py         # Destination matching agent
├── poi_agent.py             # POI discovery agent
├── event_agent.py           # Event discovery agent
├── weather_agent.py         # Weather forecast agent
├── travel_advisory_agent.py # Travel advisory lookup agent
└── tools/
    ├── __init__.py
    └── web_search.py        # Shared web search tool
```

## Usage

Each agent exposes both a high-level workflow API and a lower-level
factory/runtime pattern.

### 1. High-Level API (Recommended)

```python
from datetime import date

from src.agents import (
    find_events,
    find_points_of_interest,
    get_weather_forecast,
    get_travel_advisory,
    recommend_destinations,
)
from src.api.models.customer import CustomerProfile, TravelDates

profile = CustomerProfile(
    interests=["history", "food"],
    budget="moderate",
    travel_dates=TravelDates(
        start=date(2026, 6, 10),
        end=date(2026, 6, 17),
    ),
    party_size=2,
    departure_city="Boston",
)

destinations = await recommend_destinations(profile)
pois = await find_points_of_interest(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
events = await find_events(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
weather = await get_weather_forecast(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
advisory = await get_travel_advisory(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
```

### 2. Current Factory / Runtime Pattern

```python
from agent_framework import Agent
from agent_framework_azure_ai import AzureAIClient
from azure.identity import DefaultAzureCredential

from src.config.settings import get_settings

settings = get_settings()

client = AzureAIClient(
    project_endpoint=settings.AZURE_AI_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
    model_deployment_name=settings.AZURE_AI_MODEL_DEPLOYMENT_NAME,
)

agent = Agent(
    client=client,
    instructions="You are a destination matching agent.",
    name="general-agent",
    description="Destination matching agent",
)

response = await agent.run("Find destinations for a food-focused trip.")
print(response.text)
```

The concrete factory helpers such as `create_general_agent(settings)`
wrap this same pattern for the application code.

## Authentication

Agent authentication does **not** use API keys.

- **Local development:** run `az login` so `DefaultAzureCredential`
  resolves to `AzureCliCredential`
- **Azure deployment:** the backend Container App uses its
  system-assigned managed identity
- **Configuration:** set `AZURE_AI_PROJECT_ENDPOINT` and
  `AZURE_AI_MODEL_DEPLOYMENT_NAME`; the credential is discovered
  automatically

## Web Search Tool

**File:** `src/agents/tools/web_search.py`

All agents share a web-search helper that:
- Returns structured search results with title, URL, and snippet
- Supports the search-first grounding rule used throughout the app
- Handles missing configuration and HTTP failures gracefully
- Is exposed with the `@tool` decorator from `agent-framework`

This keeps itinerary generation grounded even when agents are executed as
server-side Azure AI agents.

## Orchestration Flow

**Two-Phase Pattern:**

```
Phase 1 (Sequential):
  CustomerProfile → General Agent → destinations

Phase 2 (Concurrent Fan-Out):
  For each destination:
    ├─ POI Agent
    ├─ Event Agent
    ├─ Weather Agent
    └─ Travel Advisory Agent

Phase 3 (Fan-In / Aggregation):
  Combine all results → Itinerary response
```

Implemented in `src/orchestrator/travel_orchestrator.py`.

## System Prompts

Each agent loads a Markdown prompt from `data/prompts/`:

```
data/prompts/
├── general-agent/
│   └── system.md
├── poi-agent/
│   └── system.md
├── event-agent/
│   └── system.md
├── weather-agent/
│   └── system.md
└── travel-advisory-agent/
    └── system.md
```

Each prompt defines:
- Role and scope
- Grounding requirements
- Output expectations
- Validation rules

## Key Conventions

- **Naming:** Agent modules use snake_case file names
- **Configuration:** Project endpoint and model deployment name come from
  `src/config/settings.py`
- **Authentication:** `DefaultAzureCredential` is the only auth path for
  Azure AI calls
- **Response handling:** Agent responses are read from `.text`
- **Error handling:** Return empty list / `None` on expected failures
- **Async:** Agent APIs stay async for concurrent orchestration

## Testing

Run structure verification:

```bash
python scripts/verify_agents.py
```

To exercise real Azure AI calls:

```bash
az login
set AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
set AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
pytest tests/unit/agents tests/integration
```

Unit tests for agents live in `tests/unit/agents/`.
Integration tests live in `tests/integration/`.

## Adding a New Agent

If you add a new agent, follow this pattern:

1. Create `{agent_name}_agent.py` in `src/agents/`
2. Implement `create_{agent}_agent(settings) -> Agent`
3. Add a high-level async workflow API
4. Add a prompt in `data/prompts/{agent-name}/system.md`
5. Register shared tools as needed
6. Export the new APIs from `src/agents/__init__.py`
7. Update the orchestrator to call the new agent
8. Add unit and integration coverage

## See Also

- [docs/architecture.md](../../docs/architecture.md) — Agent design and
  orchestration
- [.squad/decisions.md](../../.squad/decisions.md) — Team decision log and architectural context
- [.squad/skills/web-search-grounding/SKILL.md](../../.squad/skills/web-search-grounding/SKILL.md) —
  Grounding pattern documentation
- [../README.md](../README.md) — `src/` overview
