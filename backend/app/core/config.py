from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # backend/app/core → project root


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ResearchPilot"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./backend/research_assistant.db"

    # Security
    secret_key: str = "researchpilot-dev-secret-key-change-in-production"

    # Mail (optional)
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: str = "noreply@researchpilot.local"

    # External APIs
    SEMANTIC_SCHOLAR_API: str = "https://api.semanticscholar.org/graph/v1"
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    ARXIV_API: str = "https://export.arxiv.org/api/query"

    # LLM
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OPENAI_API_KEY: Optional[str] = None

    # Storage
    FAISS_STORAGE_PATH: str = "data/faiss_index"
    PAPER_DIR: str = "data/papers"
    CACHE_DIR: str = "data/cache"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()