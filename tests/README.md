# Tests — Automated Testing (Backend + Frontend)

This folder contains all automated tests for the Travel Agent backend. Frontend tests are in `frontend/` (see below).

## Folder Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── fixtures/                # Test data and mock objects
│   ├── sample_customers.py  # Sample customer profiles
│   ├── sample_responses.py  # Sample API responses
│   └── mock_agents.py       # Mock agent implementations
├── unit/                    # Unit tests (test individual components)
│   ├── agents/              # Tests for agent logic
│   ├── api/                 # Tests for API models and routes
│   └── config/              # Tests for configuration loading
└── integration/             # Integration tests (test full flows)
    ├── test_orchestrator.py # Two-phase orchestration flow
    └── test_api_endpoints.py # API endpoint integration tests
```

## Running Tests

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/unit/agents/test_general_agent.py
```

**Run with verbose output:**
```bash
pytest -v
```

**Run only unit tests:**
```bash
pytest tests/unit/
```

**Run only integration tests:**
```bash
pytest tests/integration/
```

## Test Coverage

### Backend Tests (107 passing)

Current Phase 1–3 coverage:
- ✅ API models (CustomerProfile, Itinerary)
- ✅ Orchestrator initialization and two-phase flow
- ✅ Agent factory patterns and system prompt loading
- ✅ Bing Web Search tool integration
- ✅ Full orchestration flow (General Agent → POI/Event/Weather fan-out)
- ✅ API endpoint integration tests

### Infrastructure Tests (74 passing, 4 Docker build tests skipped)

Phase 5 coverage:
- ✅ Bicep template validation (all 5 modules)
- ✅ Azure resource declarations (Container Apps, ACR, OpenAI, Bing Search)
- ✅ Parameter file syntax and schema
- ✅ Secret wiring and environment variables
- ✅ Dev/prod configuration separation
- ⊘ Docker build tests (skipped without Docker daemon)

To run infra tests:
```bash
pytest infra/tests/               # All tests
pytest infra/tests/ -m "not docker_build"  # Exclude Docker build tests
```

### Frontend Tests (66 passing)

Located in `frontend/` with 8 test files:
- ✅ Component rendering tests (CustomerForm, ItineraryView, DestinationCard, LoadingState, ErrorState)
- ✅ useItinerary hook state machine tests (idle → loading → success/error transitions)
- ✅ API client tests (createItinerary, getHealth)
- ✅ Form validation and error handling
- ✅ Accessibility tests (ARIA labels, keyboard navigation)

To run frontend tests:
```bash
cd frontend
npm run test                    # Run all tests
npm run test -- --coverage     # With coverage report
npm run test -- --watch        # Watch mode
```

**Total: 247 tests passing (107 backend + 74 infrastructure + 66 frontend)**

## What to Test

- **API Contracts:** Request/response schemas are valid Pydantic models
- **Orchestration Flow:** General → POI/Event/Weather fan-out works correctly
- **Agent Initialization:** Agents load system prompts and tools correctly
- **Configuration:** Environment variables are loaded and validated
- **Edge Cases:** Empty inputs, missing fields, invalid data types

## Fixtures

Common test fixtures in 	ests/conftest.py and 	ests/fixtures/:

- sample_customer_profile — Valid CustomerProfile object
- mock_general_agent — Mock General Agent
- mock_orchestrator — Mock travel orchestrator
- mock_api_client — Test HTTP client for API

Use these in your tests to avoid duplication.

## Test Organization

Tests mirror the source structure:

- Tests for src/agents/ → 	ests/unit/agents/
- Tests for src/api/ → 	ests/unit/api/
- Tests for src/orchestrator/ → 	ests/integration/

## Key Patterns

**Unit test example:**
```python
def test_customer_profile_validation():
    profile = CustomerProfile(
        name="Alice",
        interests=["hiking"],
        budget="moderate",
        trip_duration=7,
        travel_style="adventurous"
    )
    assert profile.name == "Alice"
```

**Integration test example:**
```python
@pytest.mark.asyncio
async def test_orchestration_flow(mock_orchestrator):
    result = await mock_orchestrator.build_itinerary(customer_profile)
    assert len(result.destinations) > 0
    assert all(d.pois for d in result.destinations)
```

## CI/CD Integration

These tests run in GitHub Actions on every push. See .github/workflows/ for CI configuration.

## See Also

- [README.md](../README.md) — Running tests section
- [docs/architecture.md](../docs/architecture.md) — System design
- [src/README.md](../src/README.md) — Production code to test
