# src/pipelines/ — Reusable Pipeline Code

This folder contains reusable, testable pipeline code for feature engineering, training, and inference.

## Status in MVP

**Currently unused.** This folder is preserved from the ML template but not part of the Travel Agent MVP.

It remains available for future phases when:
- Feature engineering is needed for customer profile enrichment
- Batch prediction workflows are required
- Historical data analysis is performed

## Design Principles

When pipelines are added, follow these principles:

- **Modularity:** One pipeline per file (e.g., eature_pipeline.py, inference_pipeline.py)
- **Testability:** Pure functions where possible; I/O at the edges
- **Determinism:** Same inputs + config = same outputs
- **Configuration:** Take parameters from src/config/, not hard-coded values
- **Reusability:** Write functions, not scripts

## Suggested Layout (Future)

If this folder is populated, organize it like:

```
src/pipelines/
├── feature/
│   └── customer_enrichment.py    # Enrich customer profiles with external data
├── train/
│   └── model_pipeline.py         # Train preference models (future)
├── infer/
│   └── predict_preferences.py    # Predict customer preferences (future)
└── common/
    └── validators.py            # Shared validation utilities
```

## Relationship to Other Components

- **Agents:** src/agents/ orchestrates work; pipelines do data processing
- **Entry points:** ntrypoints/ calls pipeline functions
- **Tests:** 	ests/pipelines/ covers pipeline logic
- **Configuration:** Pipelines accept config from src/config/settings.py

## Example (For Future Reference)

When features are added, pipelines might look like:

```python
def enrich_customer_profile(profile: CustomerProfile, config: Settings) -> EnrichedProfile:
    \"\"\"Enrich a customer profile with external data.\"\"\"
    # Fetch additional data from APIs
    # Validate inputs
    # Return enriched profile
    return enriched
```

## How This Fits

- Called by agents and entry points
- Uses configuration from src/config/
- Produces outputs written to data/ or databases
- Tested via 	ests/

## See Also

- [../README.md](../README.md) — src/ overview
- [../../entrypoints/README.md](../../entrypoints/README.md) — Entry points
- [../../tests/README.md](../../tests/README.md) — Testing strategy
