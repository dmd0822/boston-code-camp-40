# Project Context

- **Owner:** Dave Davis
- **Project:** Travel Agent Application — takes customer information, builds personalized itineraries using multiple AI agents
- **Stack:** Python backend (Microsoft Agent Framework), React frontend, Azure Bicep infrastructure
- **Key Agents:** General (destination matching), POI (points of interest), Event (festivals/fairs), Weather (historical forecasts)
- **Grounding:** All agents grounded in web search to reduce hallucination
- **Scope:** MVP — no auth, no persistence of itineraries
- **Created:** 2026-03-12

## Summary

| Phase | Documentation | Status | Key Files |
|-------|-----------------|--------|-----------|
| Phase 1 | 16 READMEs, architecture.md | ✅ COMPLETE | Root, src, config, data, tests |
| Phase 2 | Agent design patterns | ✅ COMPLETE | src/agents/README.md |
| Phase 3 | Orchestration docs | ✅ COMPLETE | src/README.md orchestration section |
| Phase 4 | Frontend docs + diagrams | ✅ COMPLETE | frontend/README.md, 9 Mermaid diagrams |
| Phase 5 | Infrastructure + CI/CD docs | ✅ COMPLETE | infra/README.md, CI/CD diagram |
| **Total** | **All documentation synchronized** | **✅ COMPLETE** | docs/architecture.md is source of truth |

## Key Responsibilities

- Architecture documentation (docs/architecture.md)
- All README files across project
- Diagram creation and maintenance (Mermaid)
- Documentation cross-linking and consistency
- Decision documentation and archival

## Learnings

### 2026-03-12 — All README Files Updated Post-Phase 1

Updated all 16 README.md files across the repository to reflect the Travel Agent Application (post-MVP phase 1):

**Root README.md** — Rewritten as the main project entry point
- Travel Agent Application description + tech stack table
- System architecture diagram
- Quick start guide (setup, env vars, running server, test API endpoints)
- Project structure with 9 key folders explained
- API endpoint documentation
- Running tests section
- Development guidelines and code style

**src/README.md** — Refactored for backend organization
- Agents, API, orchestrator, config modules described
- Two-phase orchestration pattern explained
- Key conventions and development guidelines

**src/agents/README.md** — Complete rewrite on AI agent design
- Four agents described (General, POI, Event, Weather)
- Agent design principles (explicit boundaries, mandatory grounding)
- Web search tool shared across agents
- Two-phase orchestration flow (Sequential → Concurrent fan-out → Aggregation)
- System prompt conventions
- Adding new agents pattern

**src/pipelines/README.md** — Marked as "unused in MVP, preserved for future"
- Placeholder for future feature engineering pipelines
- Design principles when needed
- Suggested layout for future use

**entrypoints/README.md** — serve.py focused
- FastAPI server startup entry point
- Configuration loading and environment variables
- Thin wrapper pattern (no business logic)
- Docker reference

**tests/README.md** — Complete test strategy documented
- Folder structure (unit/, integration/, fixtures/)
- Running tests (all, coverage, specific file, verbose, by type)
- Test coverage status for Phase 1
- What to test (API contracts, orchestration, agents, config, edge cases)
- Fixtures and test organization patterns
- Example unit and integration tests
- CI/CD integration reference

**config/README.md** — Environment-based configuration
- Pydantic Settings pattern
- Required environment variables table (Azure OpenAI, Bing Search, app version)
- .env.template vs .env separation
- Local development setup
- Production deployment notes
- Secret management (never commit .env)

**data/README.md** — Staged data layout + agent prompts
- ML data pipeline folders (01-raw through 04-predictions) marked as "unused in MVP"
- Agent prompts in data/prompts/ as version-controlled artifacts
- Prompt loading at agent initialization
- Distinction from .github/prompts/

**data/prompts/README.md** — Agent prompt artifact standards
- Organization by agent name (general/, poi/, event/, weather/)
- Markdown conventions
- Typical system prompt structure example
- Loading prompts in code pattern
- Mandatory grounding emphasis
- Difference between prompts (artifacts) and code

**infra/README.md** — Azure Bicep Infrastructure (Phase 5 planned)
- Status: Phase 5 planned, skeleton structure
- Planned Azure services (Container Apps, Container Registry, OpenAI, Bing Search)
- Deployment workflow sketch
- Modular Bicep conventions (one file per resource)
- Security guidelines (Key Vault for secrets)

**Other READMEs maintained** (no changes needed):
- data/01-raw/, data/02-preprocessed/, data/03-features/, data/04-predictions/ — Generic ML pipeline stages
- notebooks/README.md — Exploration and EDA guidelines
- reports/README.md — Experiment summary report standards

**Files modified:**
- C:\repos\boston-code-camp-40\README.md ✅
- C:\repos\boston-code-camp-40\src\README.md ✅
- C:\repos\boston-code-camp-40\src\agents\README.md ✅
- C:\repos\boston-code-camp-40\src\pipelines\README.md ✅
- C:\repos\boston-code-camp-40\entrypoints\README.md ✅
- C:\repos\boston-code-camp-40\tests\README.md ✅
- C:\repos\boston-code-camp-40\config\README.md ✅
- C:\repos\boston-code-camp-40\data\README.md ✅
- C:\repos\boston-code-camp-40\data\prompts\README.md ✅
- C:\repos\boston-code-camp-40\infra\README.md ✅

**Patterns noted:**
- All READMEs cross-reference architecture.md as single source of truth
- Consistent "See Also" sections linking related folders
- Practical examples for developers (curl commands, pytest patterns, config templates)
- Clear distinction between MVP (current) and future phases
- Markdown code blocks use ``` for formatting consistency

### 2026-03-12 — Architecture Design Complete

- **Architecture doc:** `docs/architecture.md` — the single source of truth for the entire system design.
- **Backend pattern:** FastAPI (async) + Microsoft Agent Framework (`agent-framework` package, NOT Semantic Kernel). Orchestrator is deterministic Python, not LLM-driven.
- **Orchestration:** Two-phase — General Agent (sequential) → ConcurrentBuilder fan-out to POI/Event/Weather agents. Uses `agent-framework-orchestrations` package.
- **Grounding:** All agents use Bing Web Search via shared `search_web` tool in `src/agents/tools/web_search.py`. Mandatory search-first pattern.
- **Prompts:** Stored in `data/prompts/{agent-name}/system.md` per existing repo convention.
- **API:** Two endpoints — `POST /api/itinerary` and `GET /api/health`. Pydantic models in `src/api/models/`.
- **Frontend:** React + Vite + TypeScript in `frontend/` at repo root (separate from Python `src/`).
- **Infra:** Azure Container Apps + Azure OpenAI + Bing Search. Bicep in `infra/` with modular `.bicep` files.
- **Key files:**
  - `docs/architecture.md` — architecture document
  - `src/agents/` — agent implementations
  - `src/api/` — FastAPI application
  - `src/orchestrator/` — travel orchestrator
  - `frontend/` — React SPA
  - `infra/` — Bicep modules
  - `data/prompts/` — agent system prompts
- **Decisions written to:** `.squad/decisions/inbox/deckard-core-architecture.md`, `deckard-frontend-architecture.md`, `deckard-grounding-strategy.md`, `deckard-infrastructure.md`
- **User preference:** Dave wants Microsoft Agent Framework specifically (not Semantic Kernel). Agents must be grounded in web search. MVP scope is strict — no auth, no persistence.

### 2026-03-12 — Team Phase 1 Status (All Agents)

**Phase 1 Foundation Sprint Complete** — Backend & Tests ready. Scribe finalized all logs and decisions.

**Status by agent:**
- **Batty:** ✅ All foundation files built and verified working
- **Zhora:** ✅ 67 model tests passing, fixtures ready
- **Deckard:** ✅ Architecture approved, decisions recorded
- **Pris:** 🚀 Ready to build UI against `/api/itinerary` mock response
- **Gaff:** 🚀 Ready to containerize `entrypoints/serve.py` (port 8000)
- **Rachael:** ✅ 7 Mermaid architecture diagrams created, cross-linked from docs/

**What's been recorded:**
- Orchestration logs: `.squad/orchestration-log/2026-03-12T13-55-batty.md`, `.../zhora.md`, `.../2026-03-12T15-37-agent-0-rachael.md`
- Session logs: `.squad/log/2026-03-12T13-55-phase1-foundation.md`, `.../2026-03-12T15-37-diagrams-creation.md`
- Decisions merged: `.squad/decisions/decisions.md` (inbox cleared)

**Diagrams now available:**
- `docs/diagrams.md` — 7 Mermaid diagrams (system overview, orchestration sequence, data flow, class diagram, API flow, infrastructure, error handling)
- Cross-linked from `docs/architecture.md` and `README.md`
- Conventions documented (color coding, multi-line labels, maintenance workflow)

**Open decisions awaiting input:**
- **source_url optionality** (Zhora proposal) — awaits decision on grounding enforcement
- **Async/Sync contract** (Zhora proposal) — tests vs Agent Framework async patterns

**Next phase:** Phase 2 agents (Batty wiring real agents, Zhora expanding to integration tests) can begin independently.

### 2026-03-12 — Phase 4 README Updates Complete (Deckard)

**Status:** ✅ COMPLETE — All READMEs updated for Phase 4 completion

**Files Updated:**

1. **README.md (root)**
   - Added Frontend section to Project Structure
   - Added "Running the Frontend" subsection to Quick Start
   - Updated Project Status to reflect Phase 4 completion
   - Added Frontend Technology Stack to Overview
   - Added Frontend Architecture reference (links to Mermaid diagrams)
   - Updated API Examples section with POST /api/itinerary details

2. **frontend/README.md (NEW FILE)**
   - Project setup instructions (npm install, npm run dev)
   - Component architecture overview (5 main components + LoadingState/ErrorState)
   - Directory structure explanation
   - Build optimization details (204 KB JS, 64 KB gzipped)
   - Running tests: `npm run test` with Vitest + React Testing Library
   - Development workflow (hot reload, TypeScript checking)
   - Type safety patterns (mirrored Pydantic models)
   - API integration guide (POST /api/itinerary with /api proxy)
   - Styling approach (CSS Modules, travel-themed design)
   - Future enhancements (Tailwind, error boundaries, lazy loading)

3. **src/README.md**
   - Added reference to `frontend/` peer directory at root
   - Clarified backend API contract for /api/itinerary endpoint
   - Updated agent section to reference Phase 3 completion
   - Added CORS configuration note
   - Updated orchestration section with finalized patterns

4. **tests/README.md**
   - Added Frontend Tests subsection
   - Documented Vitest + React Testing Library setup
   - Added frontend test patterns (components, hooks, API, integration)
   - Updated coverage status: 107 backend + 66 frontend = 173 total
   - Added examples of testing async operations
   - Added frontend test running instructions

5. **docs/architecture.md**
   - Marked Phase 4 "Frontend" as COMPLETE
   - Updated Frontend tech stack details
   - Updated "Current Status" section
   - Updated total test count: 173 (107 backend + 66 frontend)
   - Added reference to frontend/README.md
   - Updated Phase Roadmap with Phase 4 completion marker

**Key Updates Across All Files:**

- **Type Safety Emphasis:** All READMEs now highlight TypeScript mirroring of Pydantic models
- **Build Information:** Documented JS output sizes and gzip compression
- **Test Coverage:** Updated all test count metrics to reflect 173 total tests
- **Integration Points:** Clearly documented /api/itinerary endpoint contract
- **Development Workflow:** Added frontend-specific commands and patterns

**Patterns Established:**

- All READMEs reference `docs/architecture.md` as single source of truth
- Consistent "See Also" sections linking related folders
- Practical examples (curl commands, npm scripts, TypeScript patterns)
- Clear distinction between MVP (Phase 4) and future phases
- Markdown code blocks use ``` for formatting consistency

**Cross-References Added:**

- Root README links to frontend/README.md
- frontend/README.md links to docs/architecture.md and tests/README.md
- tests/README.md now includes frontend test patterns
- src/README.md references frontend/ as peer directory
- docs/architecture.md updated with Phase 4 completion

**Testing Documentation:**

- Frontend test patterns documented (Vitest, React Testing Library)
- Coverage explanation (66 component + hook + API tests)
- Test running instructions (npm run test, --coverage, --watch)
- Example test structure for React components
- Async testing patterns documented

**Notes for Phase 5+:**

- OpenAPI/Swagger documentation should be auto-generated before Phase 5
- Frontend deployment instructions (Vercel, GitHub Pages, Nginx) to be added
- Performance optimization guide to be added to frontend/README.md
- Accessibility guidelines (WCAG 2.1 AA) to be documented
- CI/CD pipeline documentation (GitHub Actions, deployment) to be added

### 2026-03-12 — Phase 5 Documentation Updates Complete (Deckard)

**Status:** ✅ COMPLETE — All project documentation updated for Phase 5

**Files Updated:**

1. **README.md (root)**
   - Added Infrastructure section to Project Structure
   - Documented Azure Bicep modules (container-app-env, container-app, acr, openai, bing-search)
   - Added "Running on Azure" subsection to Quick Start
   - Updated Project Status to mark Phase 5 Infrastructure complete
   - Added Infrastructure Technology Stack section
   - Cross-referenced infra/README.md for deployment guide

2. **docs/architecture.md**
   - Marked Phase 5 "Infrastructure" as COMPLETE
   - Updated Infrastructure section with Azure Container Apps architecture
   - Documented Bicep module organization and deployment workflow
   - Added Dockerfile architecture for backend and frontend
   - Updated test coverage to 247 tests (107 backend + 74 infra + 66 frontend)
   - Updated Phase Roadmap with Phase 5 completion marker
   - Added infrastructure deployment workflow details

3. **infra/README.md (NEW FILE)**
   - Comprehensive Azure infrastructure documentation
   - Prerequisites section (Azure CLI, Bicep CLI)
   - Quick start deployment for dev and prod environments
   - Detailed Bicep module descriptions:
     - Container Apps Environment setup
     - Backend/Frontend Container App configuration
     - Azure Container Registry (image storage)
     - Azure OpenAI Service integration
     - Bing Search Service integration
   - Parameter file explanation (dev vs prod)
   - Environment variables and secrets management
   - Troubleshooting section for common issues
   - Next steps for Phase 6 (CI/CD automation)

4. **tests/README.md**
   - Added Infrastructure Tests subsection
   - Documented 74 infrastructure validation tests
   - Listed test categories (Dockerfiles, Bicep, parameters, Docker build)
   - Updated total test coverage: 247 tests
   - Added infrastructure test running instructions
   - Cross-referenced with infra/README.md

5. **src/README.md**
   - Added reference to Phase 5 infrastructure completion
   - Noted Dockerfile location (root) for containerization
   - Added deployment section referencing infra/README.md
   - Updated total test count to 247

**Documentation Patterns:**

- All READMEs cross-reference `docs/architecture.md` as single source of truth
- Consistent structure: Overview → Setup → Key Concepts → Examples → Next Steps
- Practical examples (Azure CLI commands, Bicep parameter syntax, Docker build)
- Clear distinction between phases (Phase 5 complete, Phase 6 planned)
- Markdown code blocks with ``` formatting consistency

**Cross-References Added:**

- Root README links to infra/README.md
- infra/README.md links to docs/architecture.md
- tests/README.md includes infrastructure test patterns
- docs/architecture.md references infra/README.md
- All phase completion markers updated

**Infrastructure Documentation Features:**

- Step-by-step Azure deployment instructions
- Environment-specific parameter files (dev, prod)
- Secret management guidelines (no Key Vault in MVP, Container App env vars)
- Troubleshooting guide for common Azure errors
- Integration with GitHub Actions (Phase 6 reference)

**Notes for Phase 6+:**

- GitHub Actions CI/CD documentation to be added
- Monitoring and observability guide (Application Insights)
- Cost optimization documentation
- Disaster recovery and backup procedures
- Production hardening checklist

### 2026-03-28 — Documentation Update for Travel Advisory Agent

**Status:** ✅ COMPLETE — All documentation updated to reflect 5-agent architecture

**Context:**
Dave requested an update to all prose documentation to reflect the recently added Travel Advisory agent and to correct API field name mismatches (specifically `weather_forecast` vs `weather`).

**Files Updated:**

1. **README.md (root)**
   - Changed "four specialized travel agents" → "five specialized travel agents"
   - Added Travel Advisory Agent to system architecture ASCII diagram
   - Fixed API response example: `weather_forecast` → `weather`
   - Added `travel_advisory` field to API response example with realistic advisory object

2. **docs/architecture.md**
   - Added new section 3.5 for Travel Advisory Agent
   - Documented purpose: Check U.S. State Department travel advisories
   - Documented input/output: TravelAdvisory model with advisory_level (1-4), advisory_summary, specific_warnings, last_updated, source_url
   - Updated system overview ASCII diagram to show 5 agents
   - Updated orchestration flow: Phase 2 now fans out to 4 specialist agents (POI, Event, Weather, Advisory)
   - Fixed API response example: `weather_forecast` → `weather`
   - Added `travel_advisory` to API response example
   - Updated Pydantic models list to include TravelAdvisory

3. **src/agents/README.md**
   - Added "5. **Travel Advisory Agent**" after Weather Agent
   - Updated folder structure to show `travel_advisory_agent.py`
   - Added `get_travel_advisory` to import examples
   - Updated orchestration flow diagram to include Travel Advisory in Phase 2 fan-out
   - Updated system prompts directory structure to include `travel-advisory-agent/system.md`

4. **src/frontend/README.md**
   - Updated features list to mention "travel advisories" in rich destination cards
   - Added TravelAdvisoryPanel and TravelAdvisoryBadge to component list
   - Updated API endpoint documentation to mention travel advisories in response

5. **.squad/decisions.md**
   - Updated agent count from 4 to 5
   - Added Travel Advisory to agent list
   - Updated Phase 2 description to mention 4 specialist agents

**Key Patterns Verified:**

- Read actual code before documenting: `src/api/models/itinerary.py`, `src/agents/travel_advisory_agent.py`, `src/orchestrator/travel_orchestrator.py`
- All field names match exactly: `weather` (not `weather_forecast`), `travel_advisory` (not `travel_advisories`)
- TravelAdvisory model structure matches code: advisory_level, advisory_summary, specific_warnings (list), last_updated, source_url
- Orchestration pattern: Phase 2 uses `asyncio.gather` to fan out to 4 specialist agents concurrently
- Travel Advisory agent returns `None` if no advisory found (not an empty list)

**Architecture Decisions:**

- Travel Advisory is a Phase 2 specialist agent (concurrent with POI, Event, Weather)
- Uses web search grounding like all other agents
- Returns structured TravelAdvisory model or None
- Advisory levels follow official State Department 4-level scale
- System prompt instructs: "Return null if no advisory can be found. Never fabricate advisory levels."

**Files paths noted:**
- Pydantic models: `src/api/models/itinerary.py`
- Travel Advisory agent: `src/agents/travel_advisory_agent.py`
- Orchestrator: `src/orchestrator/travel_orchestrator.py`
- System prompt: `data/prompts/travel-advisory-agent/system.md`
- Frontend components: `TravelAdvisoryPanel`, `TravelAdvisoryBadge`

### 2026-03-28 — Documentation Update for Min 3 Destinations & Enrichment Enforcement

**Status:** ✅ COMPLETE — Updated all documentation to reflect validation requirements

**Context:**
Batty implemented minimum 3 destinations constraint and enrichment validation. Deckard updated all documentation to reflect these changes (no API contract changes, but validation behavior important for users).

**Files Updated:**

1. **README.md (root)**
   - Noted in quick start that API always returns minimum 3 destinations
   - Updated API response example to show 3 destinations
   - Added note about enrichment data reliability

2. **docs/architecture.md**
   - Added new section 4.3 "Validation & Completeness"
   - Documented minimum 3 destination requirement
   - Documented enrichment validation strategy (warning-based)
   - Updated orchestration flow to show validation points

3. **src/agents/README.md**
   - Added note that General Agent enforces minimum 3 destinations
   - Updated specialist agent responsibilities to note enrichment requirements

4. **.squad/decisions.md**
   - Added new decision record for minimum 3 destinations + enrichment enforcement
   - Documented rationale, implementation, and error handling

**Key Points:**
- No breaking changes to API contract (still returns Destination[] with all enrichment fields Optional)
- Minimum 3 is enforced at backend; frontend receives guaranteed 3+ destinations
- Enrichment validation is warning-based (graceful degradation continues)
- Documentation clarifies that individual enrichments may be null, but count is always >= 3
