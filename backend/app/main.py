from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.database import engine, Base
from app.routes.auth import router as auth_router
from app.routes.papers import router as papers_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Paper Assistant API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_router)
app.include_router(papers_router)

@app.get("/health")
def health_check():
    return {"status": "running"}