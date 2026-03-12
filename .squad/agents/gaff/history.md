# Project Context

- **Owner:** Dave Davis
- **Project:** Travel Agent Application — takes customer information, builds personalized itineraries using multiple AI agents
- **Stack:** Python backend (Microsoft Agent Framework), React frontend, Azure Bicep infrastructure
- **Key Agents:** General (destination matching), POI (points of interest), Event (festivals/fairs), Weather (historical forecasts)
- **Grounding:** All agents grounded in web search to reduce hallucination
- **Scope:** MVP — no auth, no persistence of itineraries
- **Created:** 2026-03-12

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-03-12 — Architecture Design Finalized (Deckard Lead)

**Status:** Approved and ready for implementation sprint

**Key Technical Decisions:**
- **Backend:** FastAPI + Microsoft Agent Framework (customer requirement)
- **Orchestration:** Two-phase deterministic Python (General Agent sequential → POI/Event/Weather concurrent)
- **Grounding:** Mandatory Bing Web Search for all agents (search-first pattern)
- **LLM:** Azure OpenAI (GPT-4o)
- **Frontend:** React + Vite + TypeScript
- **Infrastructure:** Azure Container Apps + Bicep IaC

**Agent Responsibilities:**
- **Gaff:** Infrastructure and deployment (Azure Bicep, containerization, CI/CD)

---

### 2026-03-12 — Phase 1 Backend Foundation Ready (Team)

**Status:** Backend code ready for containerization. Entrypoint defined.

**What Gaff should know:**
- **Docker target:** `entrypoints/serve.py` — the Uvicorn server entrypoint
- **Port:** Listens on port 8000
- **Environment variables:** See `.env.template` (Azure OpenAI, Bing Search keys, APP_VERSION)
- **Python version:** Check `requirements.txt` for dependencies (fastapi, uvicorn, pydantic-settings, etc.)
- **CMD suggestion:** `python entrypoints/serve.py` or `uvicorn src.api.app:create_app --host 0.0.0.0 --port 8000`
- **Health check:** `GET /api/health` (returns 200 with status JSON)

**Infrastructure next steps:**
- Bicep modules in `infra/` are approved (see Deckard's decisions for Azure resources: Container Apps, OpenAI, Bing Search)
- No Key Vault in MVP — secrets as Container App env vars
- Frontend can use Container Apps or Azure Static Web Apps (decision deferred)

**Reference Document:** `docs/architecture.md` (37KB, comprehensive MVP architecture)

**What This Means for Gaff:**
- Event Agent is a dedicated service within the agent framework
- Fan-out execution in concurrent phase with POI/Weather agents
- Must implement search-grounded reasoning for event discovery
- Inputs: destination, travel dates; Output: relevant events/festivals with details
- No authentication or persistence in MVP scope

### 2026-03-12 — Phase 5 Infrastructure Implementation Complete (Gaff)

**Status:** ✅ COMPLETE — Azure infrastructure fully implemented and tested

**Deliverables:**

1. **Backend Dockerfile**
   - Python 3.12-slim base image (lightweight, security-patched)
   - Uvicorn server with 4 workers configured
   - EXPOSE 8000 for container communication
   - Production-ready setup with proper signal handling

2. **Frontend Dockerfile**
   - Multi-stage Docker build (reduces final image size)
   - Stage 1: Node.js builder — runs `npm run build`
   - Stage 2: Nginx — serves built React app with static optimization
   - Uses official Node and Nginx images

3. **Nginx Configuration (nginx.conf)**
   - HTTP/1.1 Keep-Alive enabled
   - Gzip compression for static assets
   - Cache headers for assets (1 year for versioned files, 1 day for index.html)
   - SPA routing: all non-asset requests → index.html
   - Security headers (Cache-Control, X-Content-Type-Options)

4. **Bicep Infrastructure Modules** (5 modules + orchestration)
   - **container-app-env.bicep** — Container Apps Environment with workload profiles
   - **container-app.bicep** — Container App deployment (handles both backend/frontend)
   - **acr.bicep** — Azure Container Registry (image storage)
   - **openai.bicep** — Azure OpenAI Service (GPT-4o, AOAI endpoint, key)
   - **bing-search.bicep** — Bing Search Service (API key)
   - **main.bicep** — Orchestrator deploying all 6 resources with secret wiring

5. **Parameter Files**
   - **dev-parameters.json** — Development environment configuration
   - **prod-parameters.json** — Production environment configuration
   - Region: eastus2 (multi-environment ready)
   - Supports customization without Bicep editing

6. **Documentation**
   - **infra/README.md** — Comprehensive deployment guide
   - Prerequisites (Azure CLI, bicep CLI)
   - Deployment commands (dev/prod)
   - Environment variable setup
   - Troubleshooting section

**Key Architectural Decisions:**

- All Bicep modules follow single-responsibility principle
- Container Apps Environment created once, resources reference it
- Secrets (OpenAI key, Bing Search key) managed via Container App environment variables
- No Key Vault in MVP (simplified for Phase 5)
- Region parameterization for multi-region deployments
- Both backend and frontend deployed to Container Apps

**Integration Points:**

- Backend entrypoint: `entrypoints/serve.py` (Uvicorn on port 8000)
- Frontend build: React SPA output from `npm run build`
- Both images pushed to Azure Container Registry (ACR)
- Container Apps reference images from ACR
- OpenAI and Bing Search secrets wired as environment variables

**Testing Integration:**

- Works with Zhora's 74 infrastructure tests
- Dockerfile validation (content, structure)
- Bicep template validation (syntax, parameters)
- Parameter file schema validation

**Notes for Phase 6+:**

- GitHub Actions CI/CD (Leon) will automate image builds and pushes
- Monitoring via Application Insights recommended
- Network policies and virtual networks for production
- Managed identity for secure secret handling
- Key Vault integration when needed
