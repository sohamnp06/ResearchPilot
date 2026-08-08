from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# ResearchPilot/
# ├── .env
# └── RAG/
#     └── settings.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool

    HOST: str
    PORT: int

    CACHE_DIR: str
    PAPER_DIR: str

    SEMANTIC_SCHOLAR_API: str
    ARXIV_API: str

    LOG_LEVEL: str

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()