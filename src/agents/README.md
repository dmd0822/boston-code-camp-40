# src/agents/ — AI Agents

This folder contains the four specialized AI agents that power the Travel Agent Application:

1. **General Agent** — Destination matching / selection
2. **POI Agent** — Points of Interest discovery
3. **Event Agent** — Events, festivals, and cultural attractions
4. **Weather Agent** — Historical weather forecasting

## Agent Design Principles

- **Explicit boundaries:** Each agent has a defined role, inputs, and outputs
- **Grounding mandatory:** All agents use Bing Web Search as a tool (search-first pattern)
- **System prompts:** Each agent loads its system prompt from data/prompts/{agent-name}/system.md
- **Orchestration:** Agents are called by src/orchestrator/travel_orchestrator.py following a two-phase pattern

## Folder Structure

```
src/agents/
├── general_agent.py         # Destination matching agent
├── poi_agent.py             # POI discovery agent
├── event_agent.py           # Event discovery agent
├── weather_agent.py         # Weather forecast agent
└── tools/
    ├── web_search.py        # Bing Web Search tool (shared by all agents)
    └── __init__.py
```

## Web Search Tool

**File:** src/agents/tools/web_search.py

All agents use a shared search_web tool that:
- Calls Bing Web Search API (via BING_SEARCH_API_KEY)
- Returns search results with URLs (grounding for all reasoning)
- Is configured in each agent's system prompt as an available tool

This ensures **mandatory grounding**: agents search first, reason over results, never fabricate facts.

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

Each agent's system prompt is stored as Markdown in data/prompts/:

```
data/prompts/
├── general/
│   └── system.md          # "You are a destination-matching agent..."
├── poi/
│   └── system.md          # "You are a POI discovery agent..."
├── event/
│   └── system.md          # "You are an event discovery agent..."
└── weather/
    └── system.md          # "You are a weather forecast agent..."
```

Agents load prompts by path at initialization.

## Key Conventions

- **Naming:** Agent modules are snake_case (e.g., general_agent.py, not GeneralAgent.py)
- **Tool definitions:** All shared tools live in 	ools/ and are imported by agents
- **Configuration:** Agent endpoints, API keys, and LLM models come from src/config/settings.py
- **Testing:** Unit tests for agents live in 	ests/unit/; integration tests in 	ests/integration/

## Adding a New Agent

If you add a new agent, follow this pattern:

1. Create {agent_name}_agent.py in src/agents/
2. Define the agent class (inherits from Microsoft Agent Framework Agent)
3. Add system prompt to data/prompts/{agent_name}/system.md
4. Register the agent in the orchestrator (src/orchestrator/travel_orchestrator.py)
5. Add unit tests in 	ests/unit/agents/
6. Add integration tests in 	ests/integration/

## See Also

- [docs/architecture.md](../../docs/architecture.md) — Agent design and orchestration
- [../README.md](../README.md) — src/ overview
- [../../data/prompts/README.md](../../data/prompts/README.md) — Prompt storage and conventions
- [../../tests/README.md](../../tests/README.md) — Testing strategy
