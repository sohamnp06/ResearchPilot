from dataclasses import dataclass

from RAG.pdf_pipeline.models import TextBlock


@dataclass
class DocumentMetadata:
    """
    Represents metadata extracted from a research paper.
    """

    title: str | None
    title_block_numbers: set[int]
    authors: list[str]
    affiliations: list[str]
    emails: list[str]
    abstract: str | None


class MetadataDetector:
    """
    Detects basic research-paper metadata from the
    first page of a structured PDF document.
    """

    def detect(
        self,
        pages: list,
    ) -> DocumentMetadata:

        if not pages:
            return DocumentMetadata(
                title=None,
                title_block_numbers=set(),
                authors=[],
                affiliations=[],
                emails=[],
                abstract=None,
            )

        first_page = pages[0]

        blocks = first_page.blocks

        # -----------------------------------------
        # Title
        # -----------------------------------------

        title_blocks = self._detect_title_blocks(
            blocks
        )

        title = self._join_blocks(
            title_blocks
        )

        # -----------------------------------------
        # Authors
        # -----------------------------------------

        authors = self._detect_authors(
            blocks,
            title_blocks,
        )

        # -----------------------------------------
        # Affiliations
        # -----------------------------------------

        affiliations = self._detect_affiliations(
            blocks
        )

        # -----------------------------------------
        # Emails
        # -----------------------------------------

        emails = self._detect_emails(
            blocks
        )

        # -----------------------------------------
        # Abstract
        # -----------------------------------------

        abstract = self._detect_abstract(
            pages
        )

        return DocumentMetadata(
            title=title,
            title_block_numbers={
                block.block_number
                for block in title_blocks
            },
            authors=authors,
            affiliations=affiliations,
            emails=emails,
            abstract=abstract,
        )

    # ==================================================
    # TITLE DETECTION
    # ==================================================

    def _detect_title_blocks(
        self,
        blocks: list[TextBlock],
    ) -> list[TextBlock]:

        candidates: list[TextBlock] = []

        for block in blocks:

            text = block.text.strip()

            if not text:
                continue

            # Title should be near the top
            # of the first page.
            if block.bbox[1] > 180:
                continue

            # Ignore email blocks.
            if "@" in text:
                continue

            font_sizes = [
                span.font_size
                for span in block.spans
                if span.font_size is not None
            ]

            if not font_sizes:
                continue

            average_size = (
                sum(font_sizes)
                / len(font_sizes)
            )

            # Large typography is a strong
            # title signal.
            if average_size >= 13:
                candidates.append(block)

        return candidates

    # ==================================================
    # AUTHOR DETECTION
    # ==================================================

    def _detect_authors(
        self,
        blocks: list[TextBlock],
        title_blocks: list[TextBlock],
    ) -> list[str]:

        if not title_blocks:
            return []

        last_title_y = max(
            block.bbox[3]
            for block in title_blocks
        )

        candidates: list[str] = []

        for block in blocks:

            # Author should appear below title.
            if block.bbox[1] <= last_title_y:
                continue

            # Restrict to the metadata area.
            if block.bbox[1] > 210:
                continue

            text = block.text.strip()

            if not text:
                continue

            # Skip email.
            if "@" in text:
                continue

            # Skip affiliations.
            if self._looks_like_affiliation(
                text
            ):
                continue

            candidates.append(text)

        # Current heuristic assumes the first
        # candidate is the author line.
        return candidates[:1]

    # ==================================================
    # AFFILIATION DETECTION
    # ==================================================

    def _detect_affiliations(
        self,
        blocks: list[TextBlock],
    ) -> list[str]:

        affiliations: list[str] = []

        keywords = (
            "university",
            "institute",
            "college",
            "laboratory",
            "lab",
        )

        for block in blocks:

            text = block.text.strip()

            if any(
                keyword in text.lower()
                for keyword in keywords
            ):
                affiliations.append(text)

        return affiliations

    # ==================================================
    # EMAIL DETECTION
    # ==================================================

    def _detect_emails(
        self,
        blocks: list[TextBlock],
    ) -> list[str]:

        emails: list[str] = []

        for block in blocks:

            text = block.text.strip()

            if "@" in text:
                emails.append(text)

        return emails

    # ==================================================
    # ABSTRACT DETECTION
    # ==================================================

    def _detect_abstract(
        self,
        pages: list,
    ) -> str | None:

        abstract_started = False

        abstract_blocks: list[str] = []

        for page in pages:

            for block in page.blocks:

                text = block.text.strip()

                # Detect abstract heading.
                if text.lower() == "abstract":

                    abstract_started = True

                    continue

                if not abstract_started:
                    continue

                # Stop when Introduction begins.
                if text.startswith(
                    "1. Introduction"
                ):
                    return " ".join(
                        abstract_blocks
                    )

                abstract_blocks.append(
                    text
                )

        if abstract_blocks:
            return " ".join(
                abstract_blocks
            )

        return None

    # ==================================================
    # AFFILIATION HELPER
    # ==================================================

    def _looks_like_affiliation(
        self,
        text: str,
    ) -> bool:

        keywords = (
            "university",
            "institute",
            "college",
            "laboratory",
            "lab",
        )

        return any(
            keyword in text.lower()
            for keyword in keywords
        )

    # ==================================================
    # BLOCK JOINING
    # ==================================================

    def _join_blocks(
        self,
        blocks: list[TextBlock],
    ) -> str | None:

        if not blocks:
            return None

        return " ".join(
            block.text.strip()
            for block in blocks
        )