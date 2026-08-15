import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import LibraryItem, Paper, PaperNote, ReaderProgress, User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["Application API"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def _parse_authors(authors_value):
    if not authors_value:
        return []
    if isinstance(authors_value, list):
        return authors_value
    if isinstance(authors_value, str):
        try:
            loaded = json.loads(authors_value)
            if isinstance(loaded, list):
                return loaded
            return [str(loaded)]
        except json.JSONDecodeError:
            return [authors_value]
    return [str(authors_value)]


def _serialize_authors(authors):
    return json.dumps(authors or [])


def _paper_to_dict(paper: Paper) -> dict:
    return {
        "id": paper.id,
        "title": paper.title,
        "authors": _parse_authors(paper.authors),
        "year": paper.year,
        "source": paper.source,
        "abstract": paper.abstract,
        "pdfUrl": paper.pdf_url,
        "citationCount": paper.citation_count,
        "references": paper.references,
        "paperId": paper.id,
        "status": paper.status,
        "filename": paper.filename,
        "createdAt": paper.created_at.isoformat() if paper.created_at else None,
        "updatedAt": paper.updated_at.isoformat() if paper.updated_at else None,
    }


def _note_to_dict(note: PaperNote) -> dict:
    return {
        "id": note.id,
        "paper_id": note.paper_id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }


def _seed_demo_papers(db: Session):
    default_papers = [
        {
            "id": "paper-transformer-demo",
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
            "year": 2017,
            "source": "arxiv",
            "abstract": "The dominant sequence transduction models are based on recurrent or convolutional layers. We propose a new simple architecture, the Transformer, based solely on attention mechanisms.",
            "pdf_url": "/pdfs/attention-is-all-you-need.pdf",
            "citation_count": 123,
            "references": 18,
            "status": "published",
            "filename": "attention-is-all-you-need.pdf",
        },
        {
            "id": "paper-bert-demo",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
            "year": 2018,
            "source": "arxiv",
            "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
            "pdf_url": "/pdfs/attention-is-all-you-need.pdf",
            "citation_count": 97,
            "references": 25,
            "status": "published",
            "filename": "attention-is-all-you-need.pdf",
        },
    ]

    for payload in default_papers:
        exists = db.query(Paper).filter(Paper.id == payload["id"]).first()
        if not exists:
            db.add(
                Paper(
                    id=payload["id"],
                    title=payload["title"],
                    authors=_serialize_authors(payload["authors"]),
                    year=payload["year"],
                    source=payload["source"],
                    abstract=payload["abstract"],
                    pdf_url=payload["pdf_url"],
                    citation_count=payload["citation_count"],
                    references=payload["references"],
                    status=payload["status"],
                    filename=payload["filename"],
                    file_path=str(UPLOAD_DIR / payload["filename"]),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            continue

        needs_refresh = False
        if exists.pdf_url != payload["pdf_url"]:
            exists.pdf_url = payload["pdf_url"]
            needs_refresh = True
        if exists.file_path != str(UPLOAD_DIR / payload["filename"]):
            exists.file_path = str(UPLOAD_DIR / payload["filename"])
            needs_refresh = True
        if exists.filename != payload["filename"]:
            exists.filename = payload["filename"]
            needs_refresh = True
        if needs_refresh:
            exists.updated_at = datetime.now(timezone.utc)

    db.commit()


@router.get("/papers/search")
def search_papers(q: str | None = None, db: Session = Depends(get_db)):
    search_term = (q or "").strip()
    if search_term:
        like_term = f"%{search_term}%"
        papers = (
            db.query(Paper)
            .filter(
                or_(
                    Paper.title.ilike(like_term),
                    Paper.abstract.ilike(like_term),
                    Paper.source.ilike(like_term),
                    Paper.authors.ilike(like_term),
                )
            )
            .order_by(Paper.created_at.desc())
            .limit(20)
            .all()
        )
    else:
        papers = db.query(Paper).order_by(Paper.created_at.desc()).limit(20).all()

    if not papers:
        _seed_demo_papers(db)
        papers = db.query(Paper).order_by(Paper.created_at.desc()).limit(20).all()

    return {"papers": [_paper_to_dict(paper) for paper in papers]}


@router.get("/papers/{paper_id}")
def get_paper_details(paper_id: str, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return _paper_to_dict(paper)


@router.post("/papers/upload", status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    name = file.filename.lower()
    if not name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    suffix = Path(file.filename).suffix or ".pdf"
    paper_id = f"paper-{uuid4().hex[:12]}"
    safe_filename = f"{paper_id}{suffix}"
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as handle:
        handle.write(contents)

    pdf_url = f"http://localhost:8000/uploads/{safe_filename}"
    record = Paper(
        id=paper_id,
        title=file.filename.removesuffix(suffix) or "Uploaded paper",
        authors=_serialize_authors([]),
        year=None,
        source="uploaded",
        abstract="Uploaded PDF ready for indexing.",
        pdf_url=pdf_url,
        citation_count=0,
        references=0,
        filename=file.filename,
        file_path=str(file_path),
        status="uploaded",
        user_id=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    existing_library_item = (
        db.query(LibraryItem)
        .filter(LibraryItem.paper_id == record.id, LibraryItem.user_id == current_user.id)
        .first()
    )
    if not existing_library_item:
        db.add(LibraryItem(paper_id=record.id, user_id=current_user.id))

    existing_progress = (
        db.query(ReaderProgress)
        .filter(ReaderProgress.paper_id == record.id)
        .first()
    )
    if existing_progress:
        if existing_progress.user_id != current_user.id:
            existing_progress.user_id = current_user.id
        existing_progress.current_page = 1
        existing_progress.last_read_at = datetime.now(timezone.utc)
    else:
        db.add(
            ReaderProgress(
                paper_id=record.id,
                user_id=current_user.id,
                current_page=1,
                last_read_at=datetime.now(timezone.utc),
            )
        )

    db.commit()

    return {
        "id": record.id,
        "title": record.title,
        "filename": record.filename,
        "status": record.status,
        "pdfUrl": record.pdf_url,
        "uploaded_at": record.created_at.isoformat(),
    }


@router.get("/library")
def get_library(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(LibraryItem)
        .filter(LibraryItem.user_id == current_user.id)
        .join(Paper, LibraryItem.paper_id == Paper.id)
        .order_by(LibraryItem.created_at.desc())
        .all()
    )
    return {"papers": [_paper_to_dict(item.paper) for item in items]}


@router.post("/library")
def add_to_library(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper_id = (payload or {}).get("paper_id")
    if not paper_id:
        raise HTTPException(status_code=400, detail="paper_id is required")

    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        _seed_demo_papers(db)
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    existing = (
        db.query(LibraryItem)
        .filter(LibraryItem.paper_id == paper_id, LibraryItem.user_id == current_user.id)
        .first()
    )
    if not existing:
        db.add(LibraryItem(paper_id=paper_id, user_id=current_user.id))
        db.commit()

    return {"paper": _paper_to_dict(paper), "added": True}


@router.delete("/library/{paper_id}")
def remove_from_library(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(LibraryItem)
        .filter(LibraryItem.paper_id == paper_id, LibraryItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")

    db.delete(item)
    db.commit()
    return {"paper_id": paper_id, "deleted": True}


@router.get("/reader")
def get_reader_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    progress = (
        db.query(ReaderProgress)
        .join(Paper, ReaderProgress.paper_id == Paper.id)
        .filter(ReaderProgress.user_id == current_user.id)
        .order_by(ReaderProgress.last_read_at.desc())
        .first()
    )
    if not progress:
        return {"paper_id": None, "current_page": 1, "last_read_at": None}
    return {
        "paper_id": progress.paper_id,
        "current_page": progress.current_page,
        "last_read_at": progress.last_read_at.isoformat(),
    }


@router.get("/reader/history")
def get_reader_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    progress_rows = (
        db.query(ReaderProgress)
        .join(Paper, ReaderProgress.paper_id == Paper.id)
        .filter(ReaderProgress.user_id == current_user.id)
        .order_by(ReaderProgress.last_read_at.desc())
        .all()
    )

    papers = []
    for item in progress_rows:
        paper_dict = _paper_to_dict(item.paper)
        paper_dict.update({
            "current_page": item.current_page,
            "last_read_at": item.last_read_at.isoformat(),
        })
        papers.append(paper_dict)

    return {"papers": papers}


@router.delete("/reader/{paper_id}")
def remove_reader_progress(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    progress = (
        db.query(ReaderProgress)
        .filter(ReaderProgress.paper_id == paper_id, ReaderProgress.user_id == current_user.id)
        .first()
    )
    if not progress:
        raise HTTPException(status_code=404, detail="Reader progress not found")

    db.delete(progress)
    db.commit()
    return {"paper_id": paper_id, "deleted": True}


@router.post("/reader/progress")
def save_reader_progress(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper_id = (payload or {}).get("paper_id")
    current_page = (payload or {}).get("current_page", 1)
    if not paper_id:
        raise HTTPException(status_code=400, detail="paper_id is required")

    if not db.query(Paper).filter(Paper.id == paper_id).first():
        _seed_demo_papers(db)

    progress = (
        db.query(ReaderProgress)
        .filter(ReaderProgress.paper_id == paper_id, ReaderProgress.user_id == current_user.id)
        .first()
    )
    if not progress:
        legacy_progress = db.query(ReaderProgress).filter(ReaderProgress.paper_id == paper_id).first()
        if legacy_progress:
            legacy_progress.user_id = current_user.id
            progress = legacy_progress
        else:
            progress = ReaderProgress(
                paper_id=paper_id,
                user_id=current_user.id,
                current_page=int(current_page),
                last_read_at=datetime.now(timezone.utc),
            )
            db.add(progress)

    progress.current_page = int(current_page)
    progress.last_read_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(progress)
    return {
        "paper_id": progress.paper_id,
        "current_page": progress.current_page,
        "last_read_at": progress.last_read_at.isoformat(),
    }


@router.get("/papers/{paper_id}/notes")
def get_paper_notes(paper_id: str, db: Session = Depends(get_db)):
    notes = db.query(PaperNote).filter(PaperNote.paper_id == paper_id).order_by(PaperNote.updated_at.desc()).all()
    return {"notes": [_note_to_dict(note) for note in notes]}


@router.post("/papers/{paper_id}/notes", status_code=status.HTTP_201_CREATED)
def create_paper_note(paper_id: str, payload: dict, db: Session = Depends(get_db)):
    if not db.query(Paper).filter(Paper.id == paper_id).first():
        raise HTTPException(status_code=404, detail="Paper not found")

    note = PaperNote(
        paper_id=paper_id,
        title=(payload or {}).get("title") or "Untitled note",
        content=(payload or {}).get("content") or "",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _note_to_dict(note)


@router.put("/papers/{paper_id}/notes")
def update_paper_note(paper_id: str, payload: dict, db: Session = Depends(get_db)):
    note_id = (payload or {}).get("id")
    if not note_id:
        raise HTTPException(status_code=400, detail="Note id is required")

    note = db.query(PaperNote).filter(PaperNote.id == note_id, PaperNote.paper_id == paper_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if "title" in payload:
        note.title = payload["title"] or "Untitled note"
    if "content" in payload:
        note.content = payload["content"] or ""
    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)
    return _note_to_dict(note)


@router.get("/health")
def health_check():
    return {"status": "running"}


@router.get("/papers")
def list_papers(db: Session = Depends(get_db)):
    _seed_demo_papers(db)
    papers = db.query(Paper).order_by(Paper.created_at.desc()).limit(20).all()
    return {"papers": [_paper_to_dict(p) for p in papers]}