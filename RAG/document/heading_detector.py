import re

from RAG.pdf_pipeline.models import TextBlock


class HeadingDetector:
    """
    Detects probable section headings using document-layout
    and typography heuristics.
    """

    NUMBERING_PATTERN = re.compile(
        r"^\s*(?:"
        r"\d+(?:\.\d+)*"
        r"|[IVXLCDM]+"
        r"|[A-Z]"
        r")[\.\)]?\s+\S+",
        re.IGNORECASE,
    )

    def __init__(
        self,
        minimum_score: float = 0.55,
    ) -> None:
        self.minimum_score = minimum_score

    def is_heading(
        self,
        block: TextBlock,
        page_blocks: list[TextBlock],
    ) -> bool:
        """
        Determine whether a text block is likely to be a heading.
        """

        score = self._calculate_score(
            block,
            page_blocks,
        )

        return score >= self.minimum_score

    def score(
        self,
        block: TextBlock,
        page_blocks: list[TextBlock],
    ) -> float:
        """
        Return the heading confidence score.
        """

        return self._calculate_score(
            block,
            page_blocks,
        )

    def _calculate_score(
        self,
        block: TextBlock,
        page_blocks: list[TextBlock],
    ) -> float:

        score = 0.0

        text = block.text.strip()

        if not text:
            return 0.0

        # -----------------------------------------
        # 1. Font size
        # -----------------------------------------

        font_sizes = [
            span.font_size
            for page_block in page_blocks
            for span in page_block.spans
            if span.font_size is not None
        ]

        if font_sizes:
            average_font_size = (
                sum(font_sizes) / len(font_sizes)
            )

            block_font_sizes = [
                span.font_size
                for span in block.spans
                if span.font_size is not None
            ]

            if block_font_sizes:
                block_font_size = max(
                    block_font_sizes
                )

                if block_font_size >= average_font_size * 1.25:
                    score += 0.30

                elif block_font_size >= average_font_size * 1.10:
                    score += 0.15

        # -----------------------------------------
        # 2. Font style / flags
        # -----------------------------------------

        if self._has_emphasis(block):
            score += 0.20

        # -----------------------------------------
        # 3. Numbering pattern
        # -----------------------------------------

        if self.NUMBERING_PATTERN.match(text):
            score += 0.25

        # -----------------------------------------
        # 4. Short text
        # -----------------------------------------

        word_count = len(text.split())

        if word_count <= 12:
            score += 0.10

        # -----------------------------------------
        # 5. Heading-like punctuation
        # -----------------------------------------

        if not text.endswith((".", ",", ";", ":")):
            score += 0.05

        # -----------------------------------------
        # 6. Avoid paragraph-like text
        # -----------------------------------------

        if word_count > 30:
            score -= 0.30

        # -----------------------------------------
        # 7. Avoid obvious email / URL blocks
        # -----------------------------------------

        if "@" in text or text.startswith("http"):
            score -= 0.50

        return max(
            0.0,
            min(score, 1.0),
        )

    def _has_emphasis(
        self,
        block: TextBlock,
    ) -> bool:
        """
        Detect bold/medium/heavy typography using
        font names and PDF font flags.
        """

        for span in block.spans:

            font_name = (
                span.font or ""
            ).lower()

            if any(
                keyword in font_name
                for keyword in (
                    "bold",
                    "black",
                    "heavy",
                    "medium",
                    "semibold",
                )
            ):
                return True

            # PyMuPDF font flags:
            # bit 4 = bold
            if span.flags is not None:
                if span.flags & 16:
                    return True

        return False