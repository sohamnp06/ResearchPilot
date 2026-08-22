"""
External paper search routes.

Provides:
    GET /api/search/papers?q=<query>&limit=<n>
        → Search Semantic Scholar (primary) with arXiv fallback.
        → Returns results + similar_papers when no exact match.

    POST /api/search/import
        → Import an external paper into the local database.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Paper

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["Paper Search"])


# ──────────────────────────────────────────────────────────────────────────────
# PROVIDER FACTORY
# ──────────────────────────────────────────────────────────────────────────────

def _get_semantic_scholar():
    from RAG.paper_search.providers.semantic_scholar import SemanticScholarProvider
    return SemanticScholarProvider()


def _get_arxiv():
    from RAG.paper_search.providers.arxiv import ArxivProvider
    return ArxivProvider()


def _paper_to_response(paper) -> dict:
    """Convert RAG Paper model to API response dict."""
    pdf_url = str(paper.pdf_url) if paper.pdf_url else None
    return {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "authors": [a.name for a in (paper.authors or [])],
        "year": paper.year,
        "citation_count": paper.citation_count,
        "pdf_url": pdf_url,
        "source": paper.source,
        "has_pdf": pdf_url is not None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# SEARCH PAPERS
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/papers")
async def search_papers_external(
    q: str = "",
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Search for research papers using Semantic Scholar (primary) and arXiv (fallback).

    Returns:
        {
            "query": str,
            "results": [Paper, ...],
            "total": int,
            "source": "semantic_scholar" | "arxiv",
            "similar_papers": [Paper, ...]  # when no exact match
        }
    """
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    limit = max(1, min(limit, 20))

    results = []
    source_used = None
    errors = []

    # ── Primary: Semantic Scholar ──────────────────────────────────────────
    try:
        ss = _get_semantic_scholar()
        results = await ss.search(query=query, limit=limit)
        if results:
            source_used = "semantic_scholar"
            logger.info(
                f"Semantic Scholar returned {len(results)} results for: '{query}'"
            )
    except Exception as exc:
        logger.warning(f"Semantic Scholar search failed: {exc}")
        errors.append(f"Semantic Scholar: {exc}")

    # ── Fallback: arXiv ────────────────────────────────────────────────────
    if not results:
        try:
            arxiv = _get_arxiv()
            results = await arxiv.search(query=query, limit=limit)
            if results:
                source_used = "arxiv"
                logger.info(
                    f"arXiv returned {len(results)} results for: '{query}'"
                )
        except Exception as exc:
            logger.warning(f"arXiv search failed: {exc}")
            errors.append(f"arXiv: {exc}")

    # ── No results at all ─────────────────────────────────────────────────
    if not results:
        return {
            "query": query,
            "results": [],
            "total": 0,
            "source": None,
            "similar_papers": [],
            "message": (
                "No papers found. " + " | ".join(errors)
                if errors
                else "No papers found for this query."
            ),
        }

    result_dicts = [_paper_to_response(p) for p in results]

    # ── Detect exact match ────────────────────────────────────────────────
    query_lower = query.lower()
    has_exact = any(
        query_lower in (r.get("title") or "").lower()
        for r in result_dicts
    )

    similar_papers = []
    if not has_exact and len(result_dicts) > 1:
        # First result is closest match; rest are "similar"
        similar_papers = result_dicts[1:]
        result_dicts = result_dicts[:1]

    return {
        "query": query,
        "results": result_dicts,
        "total": len(result_dicts),
        "source": source_used,
        "similar_papers": similar_papers,
        "has_exact_match": has_exact,
    }


# ──────────────────────────────────────────────────────────────────────────────
# IMPORT PAPER INTO LOCAL DATABASE
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/import")
async def import_paper(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Import an external paper (from search results) into the local database.

    Request body:
        {
            "paper_id": str,
            "title": str,
            "abstract": str,
            "authors": [str],
            "year": int,
            "citation_count": int,
            "pdf_url": str | null,
            "source": str
        }

    Returns the local Paper record.
    """
    if not payload:
        raise HTTPException(status_code=400, detail="Request body is required.")

    paper_id = (payload.get("paper_id") or "").strip()
    title = (payload.get("title") or "").strip()

    if not paper_id:
        raise HTTPException(status_code=400, detail="paper_id is required.")
    if not title:
        raise HTTPException(status_code=400, detail="title is required.")

    # Create a DB-safe local ID (prefix to avoid collision with internal IDs)
    local_id = f"ext-{paper_id[:60]}"

    # Check if already imported
    existing = db.query(Paper).filter(Paper.id == local_id).first()
    if existing:
        return _db_paper_to_dict(existing)

    import json

    authors_raw = payload.get("authors") or []
    if isinstance(authors_raw, list):
        authors_str = json.dumps(authors_raw)
    else:
        authors_str = json.dumps([str(authors_raw)])

    pdf_url = payload.get("pdf_url")
    if pdf_url:
        pdf_url = str(pdf_url)

    from app.routes.papers import _get_next_display_id

    record = Paper(
        id=local_id,
        title=title,
        authors=authors_str,
        year=payload.get("year"),
        source=payload.get("source") or "external",
        abstract=payload.get("abstract") or "",
        pdf_url=pdf_url,
        citation_count=payload.get("citation_count") or 0,
        references=0,
        status="imported",
        display_id=_get_next_display_id(db),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info(f"Imported paper: {local_id} — '{title}'")

    return _db_paper_to_dict(record)


def _db_paper_to_dict(paper: Paper) -> dict:
    import json
    authors_raw = paper.authors or "[]"
    try:
        authors = json.loads(authors_raw)
    except Exception:
        authors = [authors_raw]

    return {
        "id": paper.id,
        "title": paper.title,
        "authors": authors,
        "year": paper.year,
        "source": paper.source,
        "abstract": paper.abstract,
        "pdfUrl": paper.pdf_url,
        "citationCount": paper.citation_count,
        "references": paper.references,
        "paperId": paper.id,
        "status": paper.status,
        "filename": paper.filename,
        "displayId": paper.display_id,
    }
