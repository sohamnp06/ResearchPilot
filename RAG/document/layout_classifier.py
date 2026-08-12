from __future__ import annotations

import re

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class LayoutClassifier:
    """
    Classifies extracted PDF blocks into high-level
    document element types.

    This is intentionally deterministic. The LLM is not
    involved in document parsing.
    """

    FIGURE_PATTERN = re.compile(
        r"^\s*(figure|fig\.?)\s*\d+",
        re.IGNORECASE,
    )

    TABLE_PATTERN = re.compile(
        r"^\s*table\s*\d+",
        re.IGNORECASE,
    )

    REFERENCE_PATTERN = re.compile(
        r"^\s*\[\s*\d+\s*\]",
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

        element_type = (
            self._detect_type(
                clean_text
            )
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

        if self._looks_like_reference(
            text
        ):
            return ElementType.REFERENCE

        if self._looks_like_figure(
            text
        ):
            return ElementType.FIGURE

        if self._looks_like_table(
            text
        ):
            return ElementType.TABLE

        if self._looks_like_code(
            text
        ):
            return ElementType.CODE

        return ElementType.PARAGRAPH

    def _looks_like_figure(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.FIGURE_PATTERN.match(
                text
            )
        )

    def _looks_like_table(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.TABLE_PATTERN.match(
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