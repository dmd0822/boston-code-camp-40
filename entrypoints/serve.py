"""Uvicorn entry point for the Travel Agent API.

Usage:
    python entrypoints/serve.py

Thin wrapper — no business logic belongs here.
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so that `src.*`
# imports resolve regardless of the working directory.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import uvicorn  # noqa: E402

from src.api.app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "entrypoints.serve:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
