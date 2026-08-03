from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class Author(BaseModel):
    name: str


class Paper(BaseModel):
    paper_id: str
    title: str
    abstract: Optional[str] = None
    authors: List[Author] = []
    year: Optional[int] = None
    citation_count: Optional[int] = None
    pdf_url: Optional[HttpUrl] = None
    source: str