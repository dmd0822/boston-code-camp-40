---
name: "agent-orchestration"
description: "Multi-agent orchestration patterns using Microsoft Agent Framework"
domain: "ai-agents"
confidence: "high"
source: "manual — architecture design for travel agent MVP"
---

## Context

This project uses the Microsoft Agent Framework (`agent-framework`
Python package) to orchestrate multiple AI agents. The pattern
applies whenever you need a coordinator that invokes agents in a
defined sequence with parallel fan-out.

## Patterns

### Sequential-Then-Concurrent Orchestration

The orchestrator is a **plain Python class** (not an agent). It
controls flow deterministically:

1. **Phase 1 (Sequential):** Call a planning agent that produces
   a list of items to process.
2. **Phase 2 (Concurrent):** Fan-out to multiple specialist agents
   using `ConcurrentBuilder` from `agent-framework-orchestrations`.
3. **Fan-In:** Aggregate results into a single response object.

```python
from agent_framework import Agent
from agent_framework.orchestrations import ConcurrentBuilder

class TravelOrchestrator:
    async def build_itinerary(self, profile):
        # Phase 1: sequential
        destinations = await self.general_agent.run(profile)

        # Phase 2: concurrent fan-out
        workflow = ConcurrentBuilder(
            participants=[self.poi_agent, self.event_agent, self.weather_agent]
        ).build()
        details = await workflow.run(destinations)

        # Fan-in: aggregate
        return self._assemble_itinerary(destinations, details)
```

### Agent Definition Pattern

Each agent is defined in its own module under `src/agents/`:

```python
from agent_framework import Agent
from agent_framework.azure_ai import AzureOpenAIChatClient

agent = Agent(
    client=AzureOpenAIChatClient(),
    instructions=load_prompt("data/prompts/{agent}/system.md"),
    tools=[search_web],
)
```

### Mandatory Grounding via Tools

Every agent receives a `search_web` tool (Bing Web Search). The
system prompt enforces search-first behavior:

> "You MUST call the search_web tool before answering. Only include
> information found in search results. Cite source URLs."

### Prompt Storage Convention

Prompts live in `data/prompts/{agent-name}/system.md` — Markdown
files, version-controlled, one per agent. This follows the existing
repo convention in `Claud.md` and `Agent.md`.

## Examples

See `docs/architecture.md` for the full design.

Key files:
- `src/agents/general_agent.py` — General Agent (destination matching)
- `src/agents/poi_agent.py` — POI Agent
- `src/agents/event_agent.py` — Event Agent
- `src/agents/weather_agent.py` — Weather Agent
- `src/agents/tools/web_search.py` — Shared Bing Search tool
- `src/orchestrator/travel_orchestrator.py` — Orchestrator

## Anti-Patterns

- **Do NOT use Semantic Kernel.** Customer explicitly requires
  Microsoft Agent Framework (`agent-framework` package).
- **Do NOT use LLM-driven routing** for the MVP orchestrator.
  The flow is deterministic: General → [POI, Event, Weather].
- **Do NOT let agents answer without searching.** Every agent
  must call `search_web` before generating output.
- **Do NOT put prompts in Python source code.** Prompts are
  artifacts in `data/prompts/`, not inline strings.
