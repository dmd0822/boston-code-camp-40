# Rachael — History

## Project Context

- **Owner:** Dave Davis
- **Project:** Travel Agent Application for Boston Code Camp 40
- **Stack:** Python backend (Microsoft Agent Framework), React frontend, Azure Bicep infrastructure
- **Key Agents:** General (destination matching), POI (points of interest), Event (festivals), Weather (historical forecasts)
- **Architecture:** Two-phase orchestration — General Agent (sequential) → concurrent fan-out to POI/Event/Weather via asyncio.gather
- **Grounding:** All agents use Bing Web Search; mandatory search-first pattern
- **Status:** Phases 1-5 complete. 247 tests passing.

## Summary

| Phase | Diagrams | Status | Key Diagrams |
|-------|----------|--------|--------------|
| Phase 1 | 7 Mermaid | ✅ COMPLETE | System overview, orchestration sequence, data flow, class diagram, API flow, infrastructure, error handling |
| Phase 4 | +1 Mermaid | ✅ COMPLETE | Frontend component architecture |
| Phase 5 | +1 Mermaid | ✅ COMPLETE | CI/CD Deployment Pipeline |
| **Total** | **9 Mermaid** | **✅ COMPLETE** | All in docs/diagrams.md |

## Key Files

- `docs/architecture.md` — single source of truth for architecture
- `docs/diagrams.md` — 9 Mermaid diagrams with maintenance guide
- `src/orchestrator/travel_orchestrator.py` — two-phase agent pipeline
- `src/agents/` — 4 agent implementations + web search tool
- `src/api/` — FastAPI app with routes and Pydantic models
- `data/prompts/` — agent system prompts

## Learnings

### Phase 1-3 Diagram Creation (Archived)

- Created 7 Mermaid diagrams for system architecture, orchestration, data flow, class models, API flow, infrastructure, and error handling
- Established color coding: Blue (user-facing), Yellow (orchestration), Purple (agents), Red (external), Green (success)
- Used `par...and...end` for concurrent execution visualization
- Maintenance guide documented for future updates
- All cross-linked from docs/architecture.md and README.md

### 2026-03-12 — Phase 4 Frontend Component Architecture Diagram

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

**Key Insights:**
- Used `par...and...end` in sequence diagram to visually represent concurrent specialist agent execution
- Subgraphs in data flow show repeated pattern across multiple destinations
- Error handling diagram shows "partial success" philosophy (return 200 with warnings rather than 500)
- Infrastructure diagram uses dashed arrows for deployment relationships vs solid for runtime calls

(Append new learnings below this line)

### 2026-03-12 — Phase 4 Frontend Component Architecture Diagram

**Status:** ✅ COMPLETE — Frontend component diagram added to docs/diagrams.md

**Diagram Created: Frontend Component Architecture (Diagram #8)**

**Pattern:** `graph TD` (top-down flowchart)

**Purpose:** Visualize React component hierarchy, state management, and API integration flow

**Component Tree Shown:**
- **App Root** (entry point)
  - **useItinerary Hook** (state machine: idle → loading → success/error)
    - **CustomerForm** (user input collection)
      - Interest input fields
      - Budget selector
      - Travel date picker
      - Destination list selector
      - Submit button
    - **ItineraryView** (results display)
      - **DestinationCard** (per destination)
        - POI Card Collection
        - Event Card Collection
        - Weather Forecast Display
      - **LoadingState** (modal overlay during fetch)
        - Spinner animation
        - Loading message
      - **ErrorState** (modal overlay on failure)
        - Error message display
        - Retry button

**Data Flow Shown:**
- CustomerProfile (interests, budget, dates, destinations) → itineraryApi client
- POST /api/itinerary → Response (ItineraryResponse with full details)
- Response → State update in useItinerary hook
- State flows down component tree: App → useItinerary → ItineraryView → DestinationCard

**Color Coding:**
- **Blue nodes:** React components (user-facing UI elements)
- **Yellow nodes:** Custom hooks (state management)
- **Purple nodes:** API client (fetch wrapper, error handling)
- **Green edges:** Props/data flow (top-down)
- **Red edges:** Event handlers (bottom-up callbacks)

**TypeScript Types Highlighted:**
- `CustomerProfile` input shape
- `ItineraryResponse` output shape
- `Destination`, `PointOfInterest`, `Event`, `WeatherForecast` nested types
- State types: `idle | loading | success | error`

**Integration Points:**
- itineraryApi.ts: POST /api/itinerary (call to backend)
- useItinerary hook: State machine managing async operations
- CSS Modules: Travel-themed responsive styling
- Error boundaries: Graceful failure handling (recommended for future)

**Diagram #1 Updated: System Overview**

**Changes Made:**
- Added Frontend box (React 18 + Vite + TypeScript)
- Updated browser connection: Browser → Frontend (React SPA)
- Updated Frontend → Backend API (FastAPI + agents)
- Clarified "Single-page application" vs "Microservices"
- Added frontend technology stack labels

**Color Consistency:**
- Maintained existing color scheme (Blue user-facing, Yellow orchestration, Purple backend)
- New Frontend box uses consistent styling with existing components

**Maintenance Notes Added:**

**File:** `docs/diagrams.md` section "Component Architecture Maintenance"

- Version: When component hierarchy changes, regenerate diagram
- How to Update: Edit mermaid graph in docs/diagrams.md, validate syntax
- Color Convention: Component (Blue), Hook (Yellow), API (Purple)
- Naming: Use actual file names (e.g., CustomerForm, not Form)
- Testing: Run `npm run build` to verify no TypeScript errors
- Cross-reference: Update if component APIs change (props, handlers)

**Integration with Existing Diagrams:**

1. System Overview — Shows frontend as user-facing layer
2. Orchestration Sequence — Shows backend two-phase agent execution
3. Data Flow — Shows POST /api/itinerary request/response
4. Frontend Component Architecture — NEW: Details frontend internal structure
5. API Flow — Shows FastAPI routes and error handling
6. Class Diagram — Shows Pydantic models (source of TypeScript types)
7. Infrastructure — Shows deployment targets for frontend (CDN, edge)
8. Error Handling — Shows error recovery flows (frontend retry + backend partial success)

**Documentation Cross-Links:**

- Updated `docs/architecture.md` — Added "Frontend Component Architecture" to TOC and linked to diagram #8
- Updated `README.md` — Added diagram #8 reference in Architecture Decisions section
- Updated `frontend/README.md` — References diagram for component structure overview
- All diagrams appear in comprehensive `docs/diagrams.md` (now 9 diagrams total)

**Validation:**

- ✅ Mermaid syntax validated (no syntax errors)
- ✅ All component names match actual file names in `frontend/src/`
- ✅ State flow matches useItinerary hook implementation
- ✅ API endpoint matches backend OpenAPI spec
- ✅ Cross-referenced from architecture and README

**Notes for Phase 5+:**

- **E2E Test Flow** — Add diagram showing Playwright/Cypress test architecture
- **Deployment Architecture** — Frontend CDN, backend API, reverse proxy
- **Error Handling Flow** — Comprehensive error recovery (network, validation, partial data)
- **Performance Monitoring** — Telemetry, logging, error tracking architecture
- **Feature Flags** — A/B testing, gradual rollout architecture

### 2026-03-12 — Phase 5 Infrastructure Diagrams Complete (Rachael)

**Status:** ✅ COMPLETE — Architecture and CI/CD deployment diagrams updated

**Diagrams Updated:**

1. **Infrastructure Architecture Diagram (Diagram #7)**
   - Updated with real Bicep resource names:
     - Azure Container Registry (ACR)
     - Container Apps Environment
     - Backend Container App
     - Frontend Container App
     - Azure OpenAI Service
     - Bing Search Service
   - Shows complete deployment topology
   - Demonstrates data flow between services
   - Includes secret management connections
   - Color-coded for clarity (Blue: user-facing, Yellow: orchestration, Purple: backend, Red: external, Green: success)

2. **CI/CD Deployment Pipeline Diagram (NEW)**
   - Complete GitHub Actions workflow visualization
   - Build stages:
     - Source code commit trigger
     - Docker build for backend (Python 3.12)
     - Docker build for frontend (Node + Nginx)
     - Push images to Azure Container Registry
   - Deployment stages:
     - Dev environment deployment
     - Production environment deployment
   - Bicep infrastructure provisioning flow
   - Secret management (GitHub Secrets → Azure)
   - Shows end-to-end deployment pipeline
   - Includes failure points and rollback paths

**Diagram Features:**

- Clear component relationships and dependencies
- Data flow paths showing Docker build → push → deployment
- Deployment sequence for dev/prod environments
- Service integration points (OpenAI, Bing Search)
- Environment variable wiring
- CI/CD orchestration via GitHub Actions
- Automated vs manual approval gates (recommended for future)

**File Updates:**

- **docs/diagrams.md** — Added CI/CD Deployment Pipeline diagram
- **docs/architecture.md** — Updated infrastructure section with diagram references
- **README.md** — Updated Architecture Decisions section with new diagrams
- **infra/README.md** — Cross-referenced deployment diagram

**Diagram Maintenance Documentation:**

- Version control: Diagrams updated whenever infrastructure changes
- Update procedure: Edit Mermaid syntax in docs/diagrams.md
- Color conventions: Consistent with existing diagrams (Blue, Yellow, Purple, Red, Green)
- Naming: Uses actual resource names from Bicep modules
- Validation: All Mermaid syntax tested and valid
- Cross-referencing: Updated all relevant documentation

**Integration with Existing Diagrams:**

1. System Overview — Shows Azure infrastructure layer
2. Orchestration Sequence — Shows backend two-phase execution
3. Data Flow — Shows POST /api/itinerary request handling
4. Frontend Component Architecture — Shows React component structure
5. API Flow — Shows FastAPI routes and error handling
6. Class Diagram — Shows Pydantic models
7. Infrastructure Architecture — Updated with real Bicep resources
8. CI/CD Deployment Pipeline — NEW: Shows build and deployment workflow
9. Error Handling — Shows error recovery flows

**Complete Diagram Ecosystem:**

- 9 Mermaid diagrams in docs/diagrams.md
- All diagrams cross-linked from docs/architecture.md
- Consistent styling and color coding
- Maintenance guide for future updates
- Clear source attribution (derived from architecture.md)

**Documentation Cross-Links:**

- Updated `docs/architecture.md` — Infrastructure and CI/CD references
- Updated `README.md` — Architecture Decisions section
- Updated `infra/README.md` — Deployment workflow reference
- All diagrams validated for correct Mermaid syntax

**Notes for Phase 6+:**

- **Monitoring Architecture** — Add diagram for Application Insights, logging, alerting
- **Security Architecture** — Add diagram for authentication, authorization, secret management
- **Performance Architecture** — Add diagram for caching, CDN, optimization strategies
- **Disaster Recovery** — Add diagram for backup, failover, recovery procedures
- **Scaling Architecture** — Add diagram for load balancing, auto-scaling, multi-region
