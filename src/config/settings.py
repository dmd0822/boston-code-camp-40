"""Application settings loaded from environment variables.

Uses pydantic-settings to validate configuration at startup.
All secrets come from env vars — nothing is hard-coded.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Travel Agent backend.

    Reads from environment variables (or a `.env` file when
    present). Validated at startup so misconfigurations fail
    fast rather than at request time.

    Authentication uses Azure Identity (DefaultAzureCredential).
    Run ``az login`` locally or use managed identity in Azure.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Azure AI Foundry (auth via DefaultAzureCredential — no API key)
    AZURE_AI_PROJECT_ENDPOINT: Optional[str] = None
    AZURE_AI_MODEL_DEPLOYMENT_NAME: Optional[str] = None

    # Application
    APP_VERSION: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Returns:
        Settings: Validated application settings.
    """
    return Settings()
