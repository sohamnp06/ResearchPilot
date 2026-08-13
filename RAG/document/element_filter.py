from __future__ import annotations

import re

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class ElementFilter:
    """
    Determines which document elements should enter the
    normal retrieval/chunking pipeline.

    The filter combines:
    1. Element type
    2. Document metadata
    3. Structural PDF artifacts
    4. Obvious diagram/header/footer text

    Only clean research prose should reach semantic
    chunking and vector retrieval.
    """

    RETRIEVABLE_TYPES = {
        ElementType.PARAGRAPH,
    }

    METADATA_TYPES = {
        ElementType.HEADING,
        ElementType.FIGURE,
        ElementType.TABLE,
        ElementType.CAPTION,
    }

    EXCLUDED_TYPES = {
        ElementType.REFERENCE,
        ElementType.DIAGRAM,
        ElementType.CODE,
        ElementType.UNKNOWN,
    }

    ARXIV_HEADER_PATTERN = re.compile(
        r"^\s*arXiv:\S+.*\d{4}\s*$",
        re.IGNORECASE,
    )

    NUMBERED_HEADING_PATTERN = re.compile(
        r"^\s*\d+(?:\.\d+)*[\.\)]?\s+\S+"
    )

    FOOTNOTE_PATTERN = re.compile(
        r"^\s*\d+\s+"
        r"(?:code is available|"
        r"available at|"
        r"copyright|"
        r"corresponding author)",
        re.IGNORECASE,
    )

    def is_retrievable(
        self,
        element: DocumentElement,
        metadata=None,
    ) -> bool:
        """
        Return True only when the element contains
        normal research content suitable for retrieval.
        """

        if (
            element.element_type
            not in self.RETRIEVABLE_TYPES
        ):
            return False

        text = element.text.strip()

        if not text:
            return False

        # Remove known metadata.
        if self._is_metadata_text(
            text,
            metadata,
        ):
            return False

        # Remove PDF headers / footers.
        if self._is_pdf_artifact(text):
            return False

        # Remove obvious headings accidentally classified
        # as paragraphs.
        if self._looks_like_heading(text):
            return False

        # Remove very short diagram labels.
        if self._looks_like_diagram_label(
            text
        ):
            return False

        return True

    def is_metadata(
        self,
        element: DocumentElement,
    ) -> bool:
        """
        Return True for elements that should be retained
        as structural/document metadata.
        """

        return (
            element.element_type
            in self.METADATA_TYPES
        )

    def is_excluded(
        self,
        element: DocumentElement,
    ) -> bool:
        """
        Return True for elements explicitly excluded
        from the normal retrieval corpus.
        """

        return (
            element.element_type
            in self.EXCLUDED_TYPES
        )

    def filter_retrievable(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return only clean research-content elements.
        """

        return [
            element
            for element in elements
            if self.is_retrievable(
                element,
                metadata,
            )
        ]

    def filter_metadata(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return structural metadata elements.
        """

        return [
            element
            for element in elements
            if self.is_metadata(element)
        ]

    def filter_excluded(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return elements explicitly excluded from
        normal retrieval.
        """

        return [
            element
            for element in elements
            if self.is_excluded(element)
        ]

    def _is_metadata_text(
        self,
        text: str,
        metadata,
    ) -> bool:
        """
        Check whether text matches known document metadata.
        """

        if metadata is None:
            return False

        normalized = self._normalize(text)

        if (
            metadata.title
            and normalized
            == self._normalize(metadata.title)
        ):
            return True

        for author in metadata.authors:

            if (
                normalized
                == self._normalize(author)
            ):
                return True

        for affiliation in metadata.affiliations:

            if (
                normalized
                == self._normalize(affiliation)
            ):
                return True

        for email in metadata.emails:

            if (
                normalized
                == self._normalize(email)
            ):
                return True

        if normalized == "abstract":
            return True

        return False

    def _is_pdf_artifact(
        self,
        text: str,
    ) -> bool:
        """
        Detect common PDF headers, footers and footnotes.
        """

        if self.ARXIV_HEADER_PATTERN.match(
            text
        ):
            return True

        if self.FOOTNOTE_PATTERN.match(
            text
        ):
            return True

        return False

    def _looks_like_heading(
        self,
        text: str,
    ) -> bool:
        """
        Detect numbered headings that may have been
        classified as paragraphs.
        """

        if self.NUMBERED_HEADING_PATTERN.match(
            text
        ):
            return True

        return False

    def _looks_like_diagram_label(
        self,
        text: str,
    ) -> bool:
        """
        Detect short labels that commonly occur inside
        figures and diagrams.
        """

        normalized = self._normalize(text)

        diagram_labels = {
            "class prediction",
            "patch embedding",
            "transpose",
            "feed-forward layer",
            "feed-forward layer (patches)",
            "feed-forward layer (features)",
            "input image",
            "image patches",
            "features",
            "patches",
        }

        if normalized in diagram_labels:
            return True

        # Very short isolated labels are unlikely to be
        # useful semantic retrieval units.
        words = normalized.split()

        if len(words) <= 2 and len(normalized) <= 30:
            return True

        return False

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        """
        Normalize whitespace and common PDF artifacts.
        """

        text = text.strip().lower()

        text = text.replace(
            "\\@",
            "@",
        )

        text = " ".join(
            text.split()
        )

        return text