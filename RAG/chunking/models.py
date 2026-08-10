from dataclasses import dataclass


@dataclass
class Sentence:
    """
    Represents a sentence extracted from a research paper.
    """

    text: str

    page: int

    block_number: int

    sentence_index: int

    section: str | None = None

    heading: str | None = None

    bbox: tuple[float, float, float, float] | None = None


@dataclass
class SemanticChunk:
    """
    Represents a semantically coherent chunk of a research paper.
    """

    chunk_id: str

    text: str

    page_start: int

    page_end: int

    section: str | None

    heading: str | None

    sentence_start: int

    sentence_end: int

    bboxes: list[
        tuple[float, float, float, float]
    ]

    sentence_count: int

    character_count: int