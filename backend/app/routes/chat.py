"""
Chat / RAG routes.

Provides endpoints for:
    - Analyzing a paper (PDF → RAG pipeline)
    - Asking questions about a paper (Q&A)
    - Summarizing a paper
    - Extracting structured information
    - Detecting research gaps
    - Verifying citations
    - Comparing two papers
"""

import logging
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.rag_client import get_rag_client
from app.database.database import get_db
from app.database.models import Paper

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["RAG / AI"])

UPLOAD_DIR = Path("uploads")


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _get_paper_or_404(paper_id: str, db: Session) -> Paper:
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found.")
    return paper


async def _resolve_pdf_path(paper: Paper) -> Path:
    """
    Resolve the local PDF path for a paper.

    Priority:
    1. Local uploaded file (already on disk)
    2. Download from pdf_url (external URL)
    """
    # 1. Check if we have a local file
    if paper.file_path:
        local = Path(paper.file_path)
        if local.is_file():
            return local

    # Check uploads directory
    if paper.filename:
        candidate = UPLOAD_DIR / paper.filename
        if candidate.is_file():
            return candidate

    # 2. Download from PDF URL
    if paper.pdf_url:
        pdf_url = str(paper.pdf_url)
        cached_path = _get_cache_path(paper.id)
        if cached_path.is_file():
            return cached_path

        logger.info(f"Downloading PDF for paper {paper.id} from: {pdf_url}")
        try:
            async with httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(pdf_url)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"Failed to download PDF (HTTP {response.status_code}). "
                        "The PDF may not be publicly accessible."
                    ),
                )

            content = response.content
            if not content.startswith(b"%PDF"):
                raise HTTPException(
                    status_code=502,
                    detail="Downloaded content is not a valid PDF.",
                )

            cached_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = cached_path.with_suffix(".tmp")
            try:
                tmp.write_bytes(content)
                tmp.replace(cached_path)
            finally:
                if tmp.exists():
                    tmp.unlink(missing_ok=True)

            return cached_path

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"PDF download failed: {exc}",
            ) from exc

    raise HTTPException(
        status_code=404,
        detail=(
            "No accessible PDF found for this paper. "
            "Please upload the PDF manually."
        ),
    )


def _get_cache_path(paper_id: str) -> Path:
    """Return the local cache path for a downloaded PDF."""
    from app.core.config import settings
    cache_dir = Path(settings.PAPER_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_id = "".join(
        c if c.isalnum() or c in "-_." else "_"
        for c in paper_id
    )
    return cache_dir / f"{safe_id}.pdf"


# ──────────────────────────────────────────────────────────────────────────────
# ANALYZE PAPER (PDF → RAG pipeline)
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/{paper_id}/analyze")
async def analyze_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Process a paper's PDF through the full RAG pipeline.

    Steps:
    1. Locate / download PDF
    2. Extract text with PyMuPDF
    3. Split sentences
    4. Generate chunks
    5. Embed with sentence-transformers
    6. Index in per-document FAISS store
    7. Persist to disk
    """
    paper = _get_paper_or_404(paper_id, db)
    rag = get_rag_client()

    if not rag.is_initialized():
        raise HTTPException(
            status_code=503,
            detail="RAG system is initializing. Please try again in a moment.",
        )

    try:
        pdf_path = await _resolve_pdf_path(paper)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        result = await rag.process_pdf(paper_id=paper_id, pdf_path=pdf_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"PDF processing error for paper {paper_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="PDF processing failed. Check server logs for details.",
        ) from exc

    # Update paper status in DB
    paper.status = "analyzed"
    db.commit()

    return {
        "paper_id": paper_id,
        "status": "analyzed",
        **result,
    }


# ──────────────────────────────────────────────────────────────────────────────
# ASK
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/{paper_id}/ask")
async def ask_paper(
    paper_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Ask a question about an analyzed paper.

    Request body:
        { "question": "How well does the model perform?" }

    Returns:
        answer, sources (chunk_id, section, page, score, text snippet)
    """
    _get_paper_or_404(paper_id, db)

    question = (payload or {}).get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required.")

    rag = get_rag_client()
    if not rag.is_initialized():
        raise HTTPException(status_code=503, detail="RAG system is initializing.")

    if not rag.is_paper_indexed(paper_id):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Paper '{paper_id}' has not been analyzed yet. "
                "Please click 'Analyze Paper' first."
            ),
        )

    try:
        result = await rag.ask(paper_id=paper_id, question=question)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Q&A error for paper {paper_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Question answering failed.") from exc


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARIZE
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/{paper_id}/summarize")
async def summarize_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Generate a structured summary of an analyzed paper.

    Returns:
        summary (string with sections: Research Problem, Objective,
        Methodology, Experiments, Key Results, Main Findings,
        Limitations, Conclusion)
    """
    _get_paper_or_404(paper_id, db)

    rag = get_rag_client()
    if not rag.is_initialized():
        raise HTTPException(status_code=503, detail="RAG system is initializing.")

    if not rag.is_paper_indexed(paper_id):
        raise HTTPException(
            status_code=409,
            detail="Paper has not been analyzed. Please analyze first.",
        )

    try:
        result = await rag.summarize(paper_id=paper_id)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Summarization error for paper {paper_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Summarization failed.") from exc


# ──────────────────────────────────────────────────────────────────────────────
# INFORMATION EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/{paper_id}/extract")
async def extract_information(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Extract structured research information from an analyzed paper.

    Returns:
        { models, datasets, metrics, results, methods, experimental_settings }
    """
    _get_paper_or_404(paper_id, db)

    rag = get_rag_client()
    if not rag.is_initialized():
        raise HTTPException(status_code=503, detail="RAG system is initializing.")

    if not rag.is_paper_indexed(paper_id):
        raise HTTPException(
            status_code=409,
            detail="Paper has not been analyzed. Please analyze first.",
        )

    try:
        result = await rag.extract_information(paper_id=paper_id)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Extraction error for paper {paper_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Information extraction failed.") from exc


# ──────────────────────────────────────────────────────────────────────────────
# RESEARCH GAPS
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/{paper_id}/research-gaps")
async def research_gaps(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """
    Detect research gaps from an analyzed paper.

    Returns:
        { limitations, unresolved_questions, future_work, research_gaps }
    """
    _get_paper_or_404(paper_id, db)

    rag = get_rag_client()
    if not rag.is_initialized():
        raise HTTPException(status_code=503, detail="RAG system is initializing.")

    if not rag.is_paper_indexed(paper_id):
        raise HTTPException(
            status_code=409,
            detail="Paper has not been analyzed. Please analyze first.",
        )

    try:
        result = await rag.research_gaps(paper_id=paper_id)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Research gap detection error for paper {paper_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Research gap detection failed.") from exc


# ──────────────────────────────────────────────────────────────────────────────
# CITATION VERIFICATION
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/{paper_id}/verify-citations")
async def verify_citations(
    paper_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Verify whether claims in an answer are supported by the paper.

    Request body:
        { "answer": "The model achieves 86.4% accuracy on ImageNet." }

    Returns:
        { verified, claims: [{ claim, supported, sources, reason }] }
    """
    _get_paper_or_404(paper_id, db)

    answer = (payload or {}).get("answer", "").strip()
    if not answer:
        raise HTTPException(status_code=400, detail="answer is required.")

    rag = get_rag_client()
    if not rag.is_initialized():
        raise HTTPException(status_code=503, detail="RAG system is initializing.")

    if not rag.is_paper_indexed(paper_id):
        raise HTTPException(
            status_code=409,
            detail="Paper has not been analyzed. Please analyze first.",
        )

    try:
        result = await rag.verify_citations(paper_id=paper_id, answer=answer)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Citation verification error for paper {paper_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Citation verification failed.") from exc


# ──────────────────────────────────────────────────────────────────────────────
# PAPER COMPARISON
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/papers/compare")
async def compare_papers(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Compare two analyzed papers using evidence from each.

    Request body:
        { "paper_id_a": "...", "paper_id_b": "..." }

    Returns:
        { comparison: "<markdown comparison text>" }
    """
    paper_id_a = (payload or {}).get("paper_id_a", "").strip()
    paper_id_b = (payload or {}).get("paper_id_b", "").strip()

    if not paper_id_a:
        raise HTTPException(status_code=400, detail="paper_id_a is required.")
    if not paper_id_b:
        raise HTTPException(status_code=400, detail="paper_id_b is required.")
    if paper_id_a == paper_id_b:
        raise HTTPException(status_code=400, detail="paper_id_a and paper_id_b must be different.")

    _get_paper_or_404(paper_id_a, db)
    _get_paper_or_404(paper_id_b, db)

    rag = get_rag_client()
    if not rag.is_initialized():
        raise HTTPException(status_code=503, detail="RAG system is initializing.")

    if not rag.is_paper_indexed(paper_id_a):
        raise HTTPException(
            status_code=409,
            detail=f"Paper A ({paper_id_a}) has not been analyzed. Please analyze it first.",
        )
    if not rag.is_paper_indexed(paper_id_b):
        raise HTTPException(
            status_code=409,
            detail=f"Paper B ({paper_id_b}) has not been analyzed. Please analyze it first.",
        )

    try:
        result = await rag.compare_papers(
            paper_id_a=paper_id_a,
            paper_id_b=paper_id_b,
        )
        return result
    except KeyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Paper comparison error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Paper comparison failed.") from exc


# ──────────────────────────────────────────────────────────────────────────────
# RAG STATUS
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/rag/status")
def rag_status():
    """Return current RAG system status."""
    rag = get_rag_client()
    return {
        "initialized": rag.is_initialized(),
        "indexed_papers": rag.get_indexed_papers(),
        "indexed_count": len(rag.get_indexed_papers()),
    }
