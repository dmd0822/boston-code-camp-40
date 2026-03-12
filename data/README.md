# `data/`

This folder contains **versioned data artifacts** used and produced by the project.

The template uses staged subfolders to keep the ML lifecycle reproducible:

- `data/01-raw/` — raw, immutable inputs
- `data/02-preprocessed/` — cleaned/standardized datasets
- `data/03-features/` — feature artifacts
- `data/04-predictions/` — model outputs

## Agent prompts

This repo also stores **agent prompt artifacts** under:

- `data/prompts/` — Markdown prompt files used by agent code in `src/agents/`

These prompts are not “data” in the ML sense, but they are treated as **version-controlled artifacts** that agent code loads by path.

Note: `.github/prompts/` is reserved for reusable GitHub Copilot prompt templates and is not the runtime prompt store for agents.
