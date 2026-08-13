from __future__ import annotations

import re

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class LayoutClassifier:
    """
    Classifies PDF text blocks into high-level document
    element types using textual and structural signals.
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
        "super().",
    )

    DIAGRAM_KEYWORDS = (
        "transpose",
        "feed-forward layer (patches)",
        "feed-forward layer (features)",
        "patch embedding",
        "class prediction",
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
        """
        Classify a single PDF text block.
        """

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
        """
        Determine the element type using a strict
        classification hierarchy.
        """

        # 1. References
        if self._looks_like_reference(text):
            return ElementType.REFERENCE

        # 2. Figure captions
        if self._looks_like_figure_caption(text):
            return ElementType.FIGURE

        # 3. Table captions
        if self._looks_like_table_caption(text):
            return ElementType.TABLE

        # 4. Code
        if self._looks_like_code(text):
            return ElementType.CODE

        # 5. Diagram labels
        if self._looks_like_diagram(text):
            return ElementType.DIAGRAM

        # 6. Everything else is normal document text.
        return ElementType.PARAGRAPH

    def _looks_like_figure_caption(
        self,
        text: str,
    ) -> bool:
        """
        Detect figure captions such as:

        Figure 1: ...
        Fig. 2: ...
        """

        return bool(
            self.FIGURE_CAPTION_PATTERN.match(
                text
            )
        )

    def _looks_like_table_caption(
        self,
        text: str,
    ) -> bool:
        """
        Detect table captions such as:

        Table 1: ...
        Table 2. ...
        """

        return bool(
            self.TABLE_CAPTION_PATTERN.match(
                text
            )
        )

    def _looks_like_reference(
        self,
        text: str,
    ) -> bool:
        """
        Detect bibliography entries beginning with:

        [1]
        [2]
        [10]
        """

        return bool(
            self.REFERENCE_PATTERN.match(text)
        )

    def _looks_like_code(
        self,
        text: str,
    ) -> bool:
        """
        Detect actual code blocks.

        A block must contain at least two independent
        code-related signals before being classified
        as CODE.
        """

        lines = text.splitlines()

        if not lines:
            return False

        signal_count = 0

        for line in lines:

            stripped = line.strip()

            for pattern in self.CODE_PATTERNS:

                if pattern in stripped:
                    signal_count += 1
                    break

        return signal_count >= 2

    def _looks_like_diagram(
        self,
        text: str,
    ) -> bool:
        """
        Detect short isolated architectural labels.

        Normal research prose should never be classified
        as a diagram merely because it contains words such
        as 'features' or 'patches'.
        """

        normalized = text.lower().strip()

        if not normalized:
            return False

        # Long text is almost certainly prose.
        if len(normalized) > 80:
            return False

        # Do not classify complete sentences as diagrams.
        if normalized.endswith(
            (".", "?", "!")
        ):
            return False

        for keyword in self.DIAGRAM_KEYWORDS:

            if keyword in normalized:
                return True

        # Very short isolated symbols.
        if len(normalized) <= 3:

            if not any(
                char.isalnum()
                for char in normalized
            ):
                return True

        return False