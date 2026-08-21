from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# ResearchPilot/
# ├── .env
# └── RAG/
#     └── settings.py
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)


class Settings(BaseSettings):
    APP_NAME: str = "ResearchPilot"
    DEBUG: bool = False

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    CACHE_DIR: str = "data/cache"
    PAPER_DIR: str = "data/papers"
    FAISS_STORAGE_PATH: str = "data/faiss_index"

    SEMANTIC_SCHOLAR_API: str = "https://api.semanticscholar.org/graph/v1"
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    ARXIV_API: str = "https://export.arxiv.org/api/query"

    LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "meta-llama/llama-3.2-3b-instruct"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OPENAI_API_KEY: Optional[str] = None

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()