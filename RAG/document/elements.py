from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ElementType(str, Enum):
    """
    Represents the semantic/layout type of a PDF element.
    """

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TABLE = "table"
    FIGURE = "figure"
    DIAGRAM = "diagram"
    CAPTION = "caption"
    CODE = "code"
    REFERENCE = "reference"
    UNKNOWN = "unknown"


@dataclass
class DocumentElement:
    """
    Represents a classified element extracted from a PDF.

    Metadata is preserved so downstream retrieval can
    trace content back to its exact document location.
    """

    element_type: ElementType

    text: str

    page: int

    block_number: int

    bbox: tuple[float, float, float, float] | None = None

    section: str | None = None

    heading: str | None = None