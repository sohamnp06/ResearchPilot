from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PaperUploadResponse(BaseModel):
    id: str
    title: str
    filename: str
    status: str
    pdfUrl: str | None = None
    uploaded_at: datetime | None = None


class PaperSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    authors: list[str] = []
    year: int | None = None
    source: str = "arxiv"
    abstract: str = ""
    pdfUrl: str | None = None
    citationCount: int = 0


class PaperDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    authors: list[str] = []
    year: int | None = None
    source: str = "arxiv"
    abstract: str = ""
    pdfUrl: str | None = None
    citationCount: int = 0
    references: int = 0
    paperId: str | None = None
    metadata: dict[str, Any] = {}


class LibraryItemResponse(BaseModel):
    paper: PaperSummaryResponse


class ReaderProgressResponse(BaseModel):
    paper_id: str | None = None
    current_page: int = 1
    last_read_at: datetime | None = None


class NoteResponse(BaseModel):
    id: int
    paper_id: str
    title: str | None = None
    content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None