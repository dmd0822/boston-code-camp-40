# Agent.md

Operating rules for a coding agent working in this repository.

## Goals

- Make changes that keep the template coherent and beginner-friendly.
- Keep responsibilities clear between pipelines, agents, entrypoints, and data.
- Avoid introducing new dependencies unless explicitly required.

## Where things go

- **Agent code**: `src/agents/`
- **ML pipeline code**: `src/pipelines/`
- **Runnable scripts**: `entrypoints/`
- **Agent prompt artifacts**: `data/prompts/` (Markdown)
- **Staged ML artifacts**: `data/01-raw/` → `data/04-predictions/`
- **Config**: `config/`
- **Tests**: `tests/`

## Project structure (high level)

```text
.
├─ Agent.md
├─ Claud.md
├─ README.md
├─ requirements.txt
├─ config/
├─ data/
│  ├─ README.md
│  ├─ 01-raw/
│  ├─ 02-preprocessed/
│  ├─ 03-features/
│  ├─ 04-predictions/
│  └─ prompts/
│     ├─ README.md
│     └─ dev-agent/
├─ entrypoints/
├─ infra/
├─ notebooks/
├─ reports/
├─ src/
│  ├─ README.md
│  ├─ agents/
│  │  └─ README.md
│  └─ pipelines/
│     └─ README.md
└─ tests/

Note: `.github/prompts/` exists for GitHub Copilot prompt templates and is not shown above.
```

## Hard rules

1. Do not move or modify the purpose of `.github/prompts/`.
   - It is reserved for GitHub Copilot prompt templates.

2. Do not put runtime prompts in `src/`.
   - Prompts are artifacts and belong in `data/prompts/`.

3. Do not put core ML logic in `entrypoints/`.
   - Entrypoints should be thin wrappers.

4. Avoid hard-coded paths.
   - Use config or function parameters.

## Documentation rules

- Any new folder should include a README describing its responsibility.
- If you update conventions, update the root README.
- Keep markdown links working (relative links only).

## Python conventions (when adding Python code)

- Follow PEP 8.
- Use type hints.
- Add docstrings for public functions/classes.
- Prefer small, composable functions.

## Testing guidance

- If you add logic (not just docs), add or update tests under `tests/`.
- Prefer unit tests for deterministic functions.

## Suggested workflow

1. Locate the correct folder for the change.
2. Implement the minimal change.
3. Update READMEs if responsibilities or usage changed.
4. Run the smallest relevant validation (tests/lint) when applicable.
