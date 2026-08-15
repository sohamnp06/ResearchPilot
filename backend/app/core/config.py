from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    secret_key: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    class Config:
        env_file = ".env"


settings = Settings()