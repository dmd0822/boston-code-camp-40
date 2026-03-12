---
name: "project-conventions"
description: "Core conventions and patterns for this codebase"
domain: "project-conventions"
confidence: "high"
source: "manual — derived from Agent.md, Claud.md, and architecture design"
---

## Context

Travel agent application with a Python backend (Microsoft Agent
Framework), React frontend, and Azure Bicep infrastructure.

## Patterns

### File Structure

- `src/agents/` — AI agent definitions (one module per agent)
- `src/api/` — FastAPI application (routes, models)
- `src/orchestrator/` — Agent orchestration logic
- `src/config/` — App configuration (Pydantic Settings)
- `src/pipelines/` — Reusable ML pipelines (existing, unused in MVP)
- `data/prompts/` — Runtime agent prompt artifacts (Markdown)
- `frontend/` — React SPA (Vite + TypeScript)
- `infra/` — Azure Bicep IaC
- `entrypoints/` — Thin executable wrappers (e.g., Uvicorn runner)
- `tests/` — pytest tests (unit/ and integration/)
- `docs/` — Architecture and design documents

### Code Style

- Python: PEP 8, type hints, PEP 257 docstrings, max 79 chars
- Linter: `ruff`
- Test framework: `pytest` with `pytest-cov`
- Frontend: TypeScript with strict mode

### Error Handling

- Pydantic validation at API boundaries (automatic 422 responses)
- Agent failures: retry up to 2 times, then return partial result
  with error flag (not a 500)
- Use specific exception types, not bare `except:`

### Testing

- Framework: `pytest`
- Location: `tests/unit/` and `tests/integration/`
- Run: `pytest tests/ -v` or `pytest tests/ --cov=src`
- Mock LLM and Bing Search in all agent tests
- Test fixtures in `tests/fixtures/`

## Examples

See `docs/architecture.md` for the full architecture.

## Anti-Patterns

- **Do NOT put prompts in Python source.** Use `data/prompts/`.
- **Do NOT put ML/agent logic in `entrypoints/`.** Keep them thin.
- **Do NOT use Semantic Kernel.** Use `agent-framework`.
- **Do NOT hard-code paths or secrets.** Use config/env vars.
- **Do NOT move `.github/prompts/`.** Reserved for Copilot IDE.
