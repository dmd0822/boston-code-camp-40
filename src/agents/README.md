# src/agents/ — AI Agents

This folder contains the four specialized AI agents that power the 
Travel Agent Application, implemented using the Microsoft Agent 
Framework.

## Agents

1. **General Agent** — Destination matching / selection
2. **POI Agent** — Points of Interest discovery
3. **Event Agent** — Events, festivals, and cultural attractions
4. **Weather Agent** — Historical weather forecasting

## Agent Design Principles

- **Explicit boundaries:** Each agent has a defined role, inputs, 
  and outputs
- **Grounding mandatory:** All agents use Bing Web Search as a 
  tool (search-first pattern)
- **System prompts:** Each agent loads its system prompt from 
  `data/prompts/{agent-name}/system.md`
- **Async by default:** All agent functions are async for 
  concurrent orchestration
- **Type-safe:** All outputs validated with Pydantic models
- **Graceful errors:** Missing credentials or malformed responses 
  return empty lists/None, not exceptions

## Folder Structure

```
src/agents/
├── __init__.py              # Exports for all agents
├── general_agent.py         # Destination matching agent
├── poi_agent.py             # POI discovery agent
├── event_agent.py           # Event discovery agent
├── weather_agent.py         # Weather forecast agent
└── tools/
    ├── __init__.py
    └── web_search.py        # Bing Web Search tool (shared)
```

## Usage

Each agent provides two APIs:

### 1. High-Level API (Recommended)

```python
from src.agents import (
    recommend_destinations,
    find_points_of_interest,
    find_events,
    get_weather_forecast,
)
from src.api.models.customer import CustomerProfile, TravelDates
from datetime import date

# Example: Get destination recommendations
profile = CustomerProfile(
    interests=["history", "food"],
    budget="moderate",
    travel_dates=TravelDates(
        start=date(2026, 6, 10), 
        end=date(2026, 6, 17)
    ),
    party_size=2,
    departure_city="Boston",
)

destinations = await recommend_destinations(profile)
# Returns List[Destination]

# Example: Get POIs for a destination
pois = await find_points_of_interest(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
# Returns List[PointOfInterest]

# Example: Get events
events = await find_events(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
# Returns List[Event]

# Example: Get weather forecast
weather = await get_weather_forecast(
    destination_name="Lisbon",
    country="Portugal",
    travel_dates=profile.travel_dates,
)
# Returns Optional[WeatherForecast]
```

### 2. Factory Pattern (Low-Level)

```python
from src.agents import create_general_agent
from src.config.settings import get_settings

settings = get_settings()
agent = create_general_agent(settings)

# Run agent manually
response = await agent.run("Find destinations for...")
```

## Web Search Tool

**File:** `src/agents/tools/web_search.py`

All agents use a shared `search_web` tool that:
- Calls Bing Web Search API (via `BING_SEARCH_API_KEY`)
- Returns structured results with title, URL, and snippet
- Handles errors gracefully (missing creds → empty results)
- Uses `@tool` decorator from `agent-framework`

This ensures **mandatory grounding**: agents search first, reason 
over results, never fabricate facts.

## Orchestration Flow

**Two-Phase Pattern:**

```
Phase 1 (Sequential):
  CustomerProfile → General Agent → destinations: List[Destination]

Phase 2 (Concurrent Fan-Out):
  For each destination:
    ├─ POI Agent      → list of points of interest
    ├─ Event Agent    → list of events
    └─ Weather Agent  → weather forecast

Phase 3 (Fan-In / Aggregation):
  Combine all results → Itinerary response
```

Implemented in: src/orchestrator/travel_orchestrator.py

## System Prompts

Each agent's system prompt is stored as Markdown in 
`data/prompts/`:

```
data/prompts/
├── general-agent/
│   └── system.md          # Destination matching
├── poi-agent/
│   └── system.md          # POI discovery
├── event-agent/
│   └── system.md          # Event discovery
└── weather-agent/
    └── system.md          # Weather forecasting
```

Each prompt includes:
- Role definition
- **MANDATORY GROUNDING RULES** (search-first, citation, no 
  fabrication)
- Task instructions
- Output format (JSON schema)
- Validation rules

Agents load prompts by path at initialization.

## Key Conventions

- **Naming:** Agent modules are snake_case (e.g., 
  `general_agent.py`)
- **Tool definitions:** Shared tools in `tools/` with `@tool` 
  decorator
- **Configuration:** API keys and endpoints from 
  `src/config/settings.py`
- **Error handling:** Return empty list/None on error, don't crash
- **Type safety:** All outputs validated with Pydantic models
- **Async:** All agent APIs are async for concurrent execution

## Testing

Run structure verification:
```bash
python scripts/verify_agents.py
```

To test with real APIs, set environment variables:
```bash
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_DEPLOYMENT=gpt-4
BING_SEARCH_API_KEY=...
BING_SEARCH_ENDPOINT=https://api.bing.microsoft.com
```

Unit tests for agents: `tests/unit/agents/`  
Integration tests: `tests/integration/`

## Adding a New Agent

If you add a new agent, follow this pattern:

1. Create `{agent_name}_agent.py` in `src/agents/`
2. Implement factory: `create_{agent}_agent(settings) -> Agent`
3. Implement high-level API: `async {verb}_{noun}(...) -> 
   ReturnType`
4. Add system prompt to `data/prompts/{agent-name}/system.md`
5. Register tools with agent (e.g., `search_web`)
6. Export from `src/agents/__init__.py`
7. Update orchestrator to call new agent
8. Write tests

See existing agents as examples.

## See Also

- [docs/architecture.md](../../docs/architecture.md) — Agent design 
  and orchestration
- [.squad/decisions/inbox/batty-agent-framework-pattern.md](../../.squad/decisions/inbox/batty-agent-framework-pattern.md) — 
  Implementation pattern decisions
- [.squad/skills/web-search-grounding/SKILL.md](../../.squad/skills/web-search-grounding/SKILL.md) — 
  Grounding pattern documentation
- [../README.md](../README.md) — src/ overview
