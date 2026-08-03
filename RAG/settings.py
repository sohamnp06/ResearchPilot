from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_file=".env",
        extra="ignore"
    )


settings = Settings()