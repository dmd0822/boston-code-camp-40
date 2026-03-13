# Tests — Automated Testing (Backend + Frontend)

This folder contains the Python-based automated tests for the Travel
Agent backend and infrastructure. Frontend tests live in `src/frontend/`
and run with Vitest.

## Folder Structure

```
tests/
├── conftest.py                # Pytest configuration and shared fixtures
├── fixtures/                  # Test data and mock objects
│   ├── sample_customers.py    # Sample customer profiles
│   ├── sample_responses.py    # Sample API responses
│   └── mock_agents.py         # Mock agent implementations
├── infra/                     # Infrastructure validation tests
│   ├── test_bicep.py          # Bicep template and parameter validation
│   ├── test_dockerfiles.py    # Dockerfile structure checks
│   └── test_docker_build.py   # Docker build checks (skipped without Docker)
├── integration/               # Backend integration tests
│   ├── test_api_endpoints.py  # API endpoint integration tests
│   └── test_orchestrator.py   # Full orchestration flow
└── unit/                      # Backend unit tests
    ├── agents/                # Agent behavior and factory tests
    ├── api/                   # API models and route tests
    └── config/                # Settings and config loading tests
```

## Current Test Snapshot

- **Backend:** 123 passing tests
- **Infrastructure:** 109 passing checks
- **Frontend:** 66 passing tests in `src/frontend/`
- **Local validation snapshot:** 242 passed, 4 skipped

The skipped checks are the Docker build validations that require a local
Docker daemon.

## Running Tests

### Backend

```bash
pytest tests/unit tests/integration
pytest tests/unit tests/integration --cov=src --cov-report=html
pytest tests/unit/agents/test_general_agent.py
pytest tests/unit tests/integration -v
```

### Infrastructure

```bash
pytest tests/infra/
pytest tests/infra/ -m "not docker_build"
```

### Frontend

```bash
cd src/frontend
npm run test
npm run test -- --coverage
npm run test:watch
```

## Coverage Details

### Backend Coverage (123 passing)

Current backend coverage includes:
- ✅ Agent factories and Azure AI client setup
- ✅ API models and request validation
- ✅ API routes and health endpoint behavior
- ✅ Travel orchestrator fan-out / fan-in flow
- ✅ Configuration loading via Pydantic Settings
- ✅ Web search tool behavior and failure handling

### Infrastructure Coverage (109 passing, 4 skipped without Docker)

Current infrastructure coverage includes:
- ✅ Bicep module validation and template structure
- ✅ Parameter file validation for `infra/parameters/*.bicepparam`
- ✅ Managed identity and RBAC wiring assertions
- ✅ Dockerfile validation for backend and frontend containers
- ⊘ Docker image build checks when Docker is unavailable

### Frontend Coverage (66 passing)

Frontend tests live in `src/frontend/` and cover:
- ✅ Component rendering and user interaction flows
- ✅ `useItinerary` hook state transitions
- ✅ API client behavior for itinerary and health requests
- ✅ Form validation and error handling
- ✅ Accessibility expectations and keyboard navigation

## What to Test

- **API contracts:** Request and response schemas remain stable
- **Orchestration flow:** General → POI / Event / Weather fan-out works
- **Agent initialization:** Foundry client creation and prompt loading
- **Configuration:** Required environment variables are validated
- **Infrastructure:** Bicep modules, parameter files, Dockerfiles, and
  RBAC wiring stay correct
- **Frontend UX:** Form submission, loading, success, and error states

## Fixtures

Common fixtures live in `tests/conftest.py` and `tests/fixtures/`:

- `sample_customer_profile` — Valid `CustomerProfile`
- `mock_general_agent` — Mock General Agent
- `mock_orchestrator` — Mock travel orchestrator
- `mock_api_client` — Test HTTP client for API routes

Use these fixtures to keep tests concise and consistent.

## Test Organization

Tests mirror the source layout:

- `tests/unit/agents/` → `src/agents/`
- `tests/unit/api/` → `src/api/`
- `tests/integration/` → orchestrator and end-to-end backend flows
- `tests/infra/` → `infra/` plus Docker deployment assets
- `src/frontend/src/**/*.test.tsx` → frontend components, hooks, and API
  client

## CI/CD Integration

GitHub Actions runs these suites through:
- `.github/workflows/deploy-app-dev.yml`
- `.github/workflows/deploy-infra-dev.yml`

## See Also

- [README.md](../README.md) — Top-level running tests section
- [src/README.md](../src/README.md) — Production code under test
- [src/frontend/README.md](../src/frontend/README.md) — Frontend testing
  details
- [docs/architecture.md](../docs/architecture.md) — System design
