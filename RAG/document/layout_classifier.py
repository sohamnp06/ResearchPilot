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

    Classification uses textual and structural signals.
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

    DIAGRAM_KEYWORDS = (
        "transpose",
        "feed-forward layer",
        "feed forward layer",
        "patches",
        "features",
    )

    TABLE_KEYWORDS = (
        "params",
        "parameter",
        "parameters",
        "imageNet",
        "top-1",
        "top 1",
        "accuracy",
        "accuracy",
        "vit",
        "deit",
        "ff only",
        "tiny",
        "base",
        "large",
        "patch size",
    )

    def classify(
        self,
        text: str,
        page: int,
        block_number: int,
        bbox=None,
        section: str | None = None,
        heading: str | None = None,
        forced_type: ElementType | None = None,
    ) -> DocumentElement:
        """
        Classify a single text block.

        forced_type is used by DocumentElementBuilder
        when a block has already been identified as
        belonging to a table region.
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

        if forced_type is not None:
            element_type = forced_type

        else:
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

        if self._looks_like_diagram(text):
            return ElementType.DIAGRAM

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
            self.REFERENCE_PATTERN.match(text)
        )

    def _looks_like_code(
        self,
        text: str,
    ) -> bool:

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

        normalized = text.lower().strip()

        # Very short isolated labels are often
        # diagram components rather than prose.
        if len(normalized) <= 25:

            if any(
                keyword in normalized
                for keyword in self.DIAGRAM_KEYWORDS
            ):
                return True

        # Diagram labels generally lack sentence
        # punctuation and contain architectural terms.
        keyword_count = sum(
            keyword in normalized
            for keyword in self.DIAGRAM_KEYWORDS
        )

        if keyword_count >= 1:

            if not normalized.endswith(
                (".", "?", "!")
            ):
                return True

        # Isolated symbols / very short labels.
        if len(normalized) <= 5:

            if not any(
                char.isalpha()
                for char in normalized
            ):
                return True

        return False

    # --------------------------------------------------
    # TABLE REGION DETECTION
    # --------------------------------------------------

    def detect_table_blocks(
        self,
        blocks: list,
    ) -> set[int]:
        """
        Detect blocks belonging to table regions.

        A table may be extracted by PyMuPDF as many
        independent text blocks. The table caption alone
        is therefore insufficient.

        This method identifies table captions and then
        searches nearby blocks for table-like content.
        """

        table_blocks: set[int] = set()

        for index, block in enumerate(blocks):

            text = block.text.strip()

            if not text:
                continue

            if not self._looks_like_table_caption(
                text
            ):
                continue

            # The caption itself is part of the table.
            table_blocks.add(
                block.block_number
            )

            # --------------------------------------------------
            # Search blocks immediately BEFORE the caption.
            #
            # In this paper the table body is extracted
            # before the caption.
            # --------------------------------------------------

            backward_index = index - 1

            while backward_index >= 0:

                candidate = blocks[
                    backward_index
                ]

                candidate_text = (
                    candidate.text.strip()
                )

                if not candidate_text:
                    backward_index -= 1
                    continue

                if self._looks_like_table_content(
                    candidate_text
                ):
                    table_blocks.add(
                        candidate.block_number
                    )

                    backward_index -= 1
                    continue

                break

            # --------------------------------------------------
            # Search blocks immediately AFTER the caption.
            #
            # This supports PDFs where the caption appears
            # before the table body.
            # --------------------------------------------------

            forward_index = index + 1

            while forward_index < len(blocks):

                candidate = blocks[
                    forward_index
                ]

                candidate_text = (
                    candidate.text.strip()
                )

                if not candidate_text:
                    forward_index += 1
                    continue

                if self._looks_like_table_content(
                    candidate_text
                ):
                    table_blocks.add(
                        candidate.block_number
                    )

                    forward_index += 1
                    continue

                break

        return table_blocks

    def _looks_like_table_content(
        self,
        text: str,
    ) -> bool:
        """
        Determine whether a text block resembles
        tabular content rather than normal prose.
        """

        normalized = text.lower().strip()

        if not normalized:
            return False

        # Explicit table vocabulary.
        for keyword in self.TABLE_KEYWORDS:

            if keyword.lower() in normalized:
                return True

        # Table cells are usually short.
        if len(normalized) <= 40:

            # Numeric-heavy content is strongly indicative
            # of a table.
            digit_count = sum(
                char.isdigit()
                for char in normalized
            )

            if digit_count >= 1:
                return True

        # Patterns such as:
        #
        # P = 16
        # 86M 77.9
        # 5.7M 72.2
        #
        if re.search(
            r"\b\d+(?:\.\d+)?\s*[mk%]?\b",
            normalized,
        ):
            if len(normalized) <= 80:
                return True

        # Common model-size labels.
        if re.match(
            r"^\s*(tiny|small|base|large|medium)\b",
            normalized,
            re.IGNORECASE,
        ):
            return True

        return False