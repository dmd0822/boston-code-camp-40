# `data/prompts/`

This folder stores **agent prompt artifacts**.

Prompts are treated like configuration/artifacts:

- They are version-controlled
- They are referenced by agent code in `src/agents/` by path
- They should be stable, reviewable, and easy to diff

## Conventions

- Use Markdown (`.md`) for prompts.
- Keep prompts small and composable.
- Prefer one purpose per file (e.g., `system.md`, `policy.md`, `task.md`).
- Organize prompts by agent name and/or workflow.

## Suggested layout (example)

```text
data/
  prompts/
    dev-agent/
      system.md
      task.md
    research-agent/
      system.md
      tools.md
```

## Relationship to `.github/prompts/`

- `.github/prompts/` contains reusable GitHub Copilot prompt templates for IDE workflows.
- `data/prompts/` contains runtime prompt artifacts for agent code.

Keep them separate.
