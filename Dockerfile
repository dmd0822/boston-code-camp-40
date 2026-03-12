# Multi-stage build for Travel Agent Backend
FROM python:3.12-slim AS base

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY entrypoints/ ./entrypoints/
COPY data/ ./data/

# Expose port
EXPOSE 8000

# Production command — NO reload, use workers for concurrency
CMD ["uvicorn", "entrypoints.serve:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
