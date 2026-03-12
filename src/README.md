# `src/`

This folder contains **production code**.

In this repository template:

- Reusable ML pipeline logic lives in `src/pipelines/`
- Agentic development/orchestration logic lives in `src/agents/`

Keep `entrypoints/` small: it should mainly parse config/CLI arguments and call into `src/`.
