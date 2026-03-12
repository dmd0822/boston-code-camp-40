# Claud.md

Repository guidance for LLM-based assistants.

## Purpose

This repository is an ML project template that also supports **agentic development**.

- Agent implementation code lives under `src/` (specifically `src/agents/`).
- Agent prompt artifacts live under `data/` (specifically `data/prompts/`).
- Reusable GitHub Copilot prompt templates live under `.github/prompts/` and should **not** be used as runtime agent prompts.

## Repo map (high level)

- `src/pipelines/` — reusable ML pipeline code (feature/train/infer/eval)
- `src/agents/` — agent orchestration, tool routing, prompt loading/rendering
- `data/01-raw/` → `data/04-predictions/` — staged ML artifacts
- `data/prompts/` — runtime prompt artifacts for agents
- `entrypoints/` — runnable scripts (thin wrappers)
- `config/` — configuration
- `tests/` — automated tests

## Non-negotiable conventions

1. **Do not move or repurpose `.github/prompts/`**
   - Those files are reusable IDE prompt templates for GitHub Copilot.
   - Runtime agent prompts belong in `data/prompts/`.

2. **Agent code belongs in `src/agents/`**
   - Keep orchestration and prompt-handling logic here.
   - Keep ML domain logic in `src/pipelines/`.

3. **Keep I/O at the edges**
   - Entrypoints read configs/args and call into `src/` modules.
   - Pipelines/agents should be testable without requiring global state.

## Prompt artifacts (runtime)

- Store prompts as Markdown (`.md`) under `data/prompts/`.
- Prefer one purpose per file:
  - `system.md`, `policy.md`, `task.md`, `tools.md`.
- Organize by agent name/workflow:

```text
data/
  prompts/
    dev-agent/
      system.md
      task.md
```

## When you change structure

- Update the root README and the relevant folder README(s).
- Keep links relative and verify they resolve.

## What to do if uncertain

- Default to the simplest change consistent with the folder responsibilities above.
- Prefer documentation and structure improvements over speculative runtime code.
