from fastapi import FastAPI

from settings import settings
from logging_config import app_logger


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    app_logger.info(f"{settings.APP_NAME} started successfully.")


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }