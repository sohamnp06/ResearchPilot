from __future__ import annotations

import re

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class LayoutClassifier:
    """
    Classifies PDF text blocks into high-level document
    element types.

    Classification is deterministic and uses textual,
    structural, and formatting signals.
    """

    FIGURE_CAPTION_PATTERN = re.compile(
        r"^\s*(figure|fig\.?)\s*\d+\s*[:.\-]",
        re.IGNORECASE,
    )

    TABLE_CAPTION_PATTERN = re.compile(
        r"^\s*table\s*\d+\s*[:.\-]",
        re.IGNORECASE,
    )

    REFERENCE_PATTERN = re.compile(
        r"^\s*\[\s*\d+\s*\]"
    )

    CODE_PATTERNS = (
        "def ",
        "class ",
        "import ",
        "from ",
        "return ",
        "nn.",
        "torch.",
        "self.",
        "->",
    )

    def classify(
        self,
        text: str,
        page: int,
        block_number: int,
        bbox=None,
        section: str | None = None,
        heading: str | None = None,
    ) -> DocumentElement:

        clean_text = text.strip()

        if not clean_text:
            return DocumentElement(
                element_type=ElementType.UNKNOWN,
                text="",
                page=page,
                block_number=block_number,
                bbox=bbox,
                section=section,
                heading=heading,
            )

        element_type = self._detect_type(
            clean_text
        )

        return DocumentElement(
            element_type=element_type,
            text=clean_text,
            page=page,
            block_number=block_number,
            bbox=bbox,
            section=section,
            heading=heading,
        )

    def _detect_type(
        self,
        text: str,
    ) -> ElementType:

        if self._looks_like_reference(text):
            return ElementType.REFERENCE

        if self._looks_like_figure_caption(text):
            return ElementType.FIGURE

        if self._looks_like_table_caption(text):
            return ElementType.TABLE

        if self._looks_like_code(text):
            return ElementType.CODE

        return ElementType.PARAGRAPH

    def _looks_like_figure_caption(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.FIGURE_CAPTION_PATTERN.match(
                text
            )
        )

    def _looks_like_table_caption(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.TABLE_CAPTION_PATTERN.match(
                text
            )
        )

    def _looks_like_reference(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.REFERENCE_PATTERN.match(
                text
            )
        )

    def _looks_like_code(
        self,
        text: str,
    ) -> bool:

        lines = text.splitlines()

        if not lines:
            return False

        code_signal_count = 0

        for line in lines:
            stripped = line.strip()

            for pattern in self.CODE_PATTERNS:
                if pattern in stripped:
                    code_signal_count += 1
                    break

        return code_signal_count >= 2