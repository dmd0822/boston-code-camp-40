# Rachael — History

## Project Context

- **Owner:** Dave Davis
- **Project:** Travel Agent Application for Boston Code Camp 40
- **Stack:** Python backend (Microsoft Agent Framework), React frontend, Azure Bicep infrastructure
- **Key Agents:** General (destination matching), POI (points of interest), Event (festivals), Weather (historical forecasts)
- **Architecture:** Two-phase orchestration — General Agent (sequential) → concurrent fan-out to POI/Event/Weather via asyncio.gather
- **Grounding:** All agents use Bing Web Search; mandatory search-first pattern
- **Status:** Phases 1-3 complete (foundation, agents, orchestration). 107 tests passing.

## Key Files

- `docs/architecture.md` — single source of truth for architecture
- `src/orchestrator/travel_orchestrator.py` — two-phase agent pipeline
- `src/agents/` — 4 agent implementations + web search tool
- `src/api/` — FastAPI app with routes and Pydantic models
- `data/prompts/` — agent system prompts

## Learnings

### 2026-03-12 — Comprehensive Mermaid Diagram Creation

**Patterns Used:**
- **System overview**: `graph TD` (top-down flowchart) for high-level architecture with external services
- **Sequence diagrams**: `sequenceDiagram` for two-phase orchestration showing concurrent execution with `par...and...end` blocks
- **Data flow**: `graph LR` (left-right) with subgraphs to show parallel specialist agent processing
- **Class diagrams**: `classDiagram` for Pydantic model relationships using composition (`*--`) notation
- **API flow**: `graph TD` with decision nodes (`{}`) for routing and error handling
- **Infrastructure**: `graph TB` with nested subgraphs for Azure resource organization
- **Error handling**: `graph TD` with failure paths showing retry logic and partial success patterns

**File Paths:**
- Created: `docs/diagrams.md` (15KB, 7 diagrams)
- Updated: `docs/architecture.md` (added link at TOC)
- Updated: `README.md` (added link in Architecture Decisions section)

**Conventions Established:**
- Color coding: Blue (user-facing), Yellow (orchestration), Purple (agents), Red (external), Green (success)
- Consistent labeling: `<br/>` for multi-line node labels
- Source attribution: All diagrams note they derive from architecture.md
- Maintenance section: Includes update workflow and diagram conventions
- All diagrams tested for valid Mermaid syntax

**Key Insights:**
- Used `par...and...end` in sequence diagram to visually represent concurrent specialist agent execution
- Subgraphs in data flow show repeated pattern across multiple destinations
- Error handling diagram shows "partial success" philosophy (return 200 with warnings rather than 500)
- Infrastructure diagram uses dashed arrows for deployment relationships vs solid for runtime calls

(Append new learnings below this line)
