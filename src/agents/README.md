# `src/agents/`

This folder contains **agentic development code**.

In this template, “agent code” means code that:

- Plans work (task decomposition, tool selection, orchestration)
- Loads and applies prompt artifacts (stored under `data/prompts/`)
- Calls into pipeline code (`src/pipelines/`) to do domain work
- Produces outputs (files, reports, predictions) using the same conventions as the rest of the repo

## What belongs here

- Agent orchestration and routing logic
- Prompt loading and rendering utilities
- Tool wrappers and adapters (e.g., file ops, evaluation helpers)
- Agent-specific domain logic that is **not** part of a reusable ML pipeline

## What should NOT live here

- ML feature engineering, training, inference, or evaluation pipeline logic (put that in `src/pipelines/`)
- Runnable “main scripts” that are executed directly (put those in `entrypoints/`)
- Prompt text / system instructions (store those in `data/prompts/`)

## Relationship to `data/prompts/`

Agent prompts are treated as **version-controlled artifacts**.

- Prompts live in `data/prompts/`.
- Agent code in `src/agents/` loads prompts by path and applies them at runtime.

## Suggested layout (example)

```text
src/
  agents/
    common/
    dev_agent/
    research_agent/
```

## How This Fits

- Agent logic: `src/agents/`
- Prompt artifacts: `data/prompts/`
- Domain pipelines: `src/pipelines/`
- Execution wrappers: `entrypoints/`
