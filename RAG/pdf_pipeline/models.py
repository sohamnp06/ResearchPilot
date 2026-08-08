from pydantic import BaseModel


class TextSpan(BaseModel):
    text: str
    bbox: tuple[float, float, float, float]
    font: str | None = None
    font_size: float | None = None
    flags: int | None = None


class TextBlock(BaseModel):
    page: int
    block_number: int
    bbox: tuple[float, float, float, float]
    text: str
    spans: list[TextSpan]


class PageContent(BaseModel):
    page_number: int
    width: float
    height: float
    blocks: list[TextBlock]