import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root on sys.path so RAG package is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.database.database import engine, Base
from app.routes.auth import router as auth_router
from app.routes.papers import router as papers_router
from app.routes.chat import router as chat_router
from app.routes.search import router as search_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# DATABASE SETUP
# ──────────────────────────────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)


# ──────────────────────────────────────────────────────────────────────────────
# LIFESPAN (startup / shutdown)
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize shared resources at startup.
    The embedding model is loaded ONCE here so all requests reuse it.
    """
    logger.info("ResearchPilot backend starting up...")

    # Initialize RAG client (loads embedding model + LLM generator)
    try:
        from app.ai.rag_client import get_rag_client
        rag = get_rag_client()
        rag.initialize()
        logger.info("RAG client initialized successfully.")
    except Exception as exc:
        logger.error(f"RAG client initialization failed: {exc}", exc_info=True)
        logger.warning(
            "RAG features will be unavailable until the model loads. "
            "Check that sentence-transformers is installed."
        )

    # Ensure required directories exist
    for directory in ["uploads", "data/papers", "data/cache", "data/faiss_index"]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logger.info("ResearchPilot backend ready.")
    yield
    logger.info("ResearchPilot backend shutting down.")


# ──────────────────────────────────────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="ResearchPilot API",
    description="AI-powered research paper assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploaded PDFs
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth_router)
app.include_router(papers_router)
app.include_router(chat_router)
app.include_router(search_router)


@app.get("/health")
def health_check():
    from app.ai.rag_client import get_rag_client
    rag = get_rag_client()
    return {
        "status": "running",
        "rag_initialized": rag.is_initialized(),
        "indexed_papers": len(rag.get_indexed_papers()),
    }