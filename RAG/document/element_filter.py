from __future__ import annotations

import re

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class ElementFilter:
    """
    Filters document elements according to their role
    in the retrieval pipeline.

    Only meaningful research-content elements are allowed
    into semantic retrieval.
    """

    RETRIEVABLE_TYPES = {
        ElementType.PARAGRAPH,
    }

    NON_RETRIEVABLE_TYPES = {
        ElementType.FIGURE,
        ElementType.TABLE,
        ElementType.DIAGRAM,
        ElementType.CODE,
        ElementType.REFERENCE,
        ElementType.CAPTION,
        ElementType.UNKNOWN,
        ElementType.HEADING,
    }

    PAGE_NUMBER_PATTERN = re.compile(
        r"^\s*\d+\s*$"
    )

    ARXIV_PATTERN = re.compile(
        r"^\s*arXiv:",
        re.IGNORECASE,
    )

    ABSTRACT_PATTERN = re.compile(
        r"^\s*abstract\s*$",
        re.IGNORECASE,
    )

    SECTION_HEADING_PATTERN = re.compile(
        r"^\s*\d+(?:\.\d+)*[\.\)]?\s+.+$"
    )

    TITLE_FRAGMENT_PATTERN = re.compile(
        r"^(do you even need attention\?|"
        r"a stack of feed-forward layers does|"
        r"surprisingly well on imagenet)$",
        re.IGNORECASE,
    )

    DIAGRAM_LABELS = {
        "patch embedding",
        "class prediction",
        "transpose",
        "feed-forward layer",
        "feed forward layer",
        "features",
        "patches",
        "attention",
    }

    def filter_retrievable(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return only clean research-content elements
        suitable for semantic retrieval.
        """

        metadata_texts = self._get_metadata_texts(
            metadata
        )

        retrievable: list[DocumentElement] = []

        for element in elements:

            if (
                element.element_type
                not in self.RETRIEVABLE_TYPES
            ):
                continue

            text = element.text.strip()

            if not text:
                continue

            if text in metadata_texts:
                continue

            if self._is_structural_noise(text):
                continue

            if self._is_page_number(text):
                continue

            if self._is_arxiv_artifact(text):
                continue

            if self._is_section_heading(text):
                continue

            if self._is_title_fragment(text):
                continue

            if self._is_diagram_label(text):
                continue

            retrievable.append(element)

        return retrievable

    def filter_metadata(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return document metadata and structural/noise
        elements that should not enter retrieval.
        """

        metadata_texts = self._get_metadata_texts(
            metadata
        )

        metadata_elements: list[DocumentElement] = []

        for element in elements:

            text = element.text.strip()

            if not text:
                continue

            if text in metadata_texts:
                metadata_elements.append(element)
                continue

            if self._is_structural_noise(text):
                metadata_elements.append(element)
                continue

            if self._is_page_number(text):
                metadata_elements.append(element)
                continue

            if self._is_arxiv_artifact(text):
                metadata_elements.append(element)
                continue

            if self._is_section_heading(text):
                metadata_elements.append(element)
                continue

            if self._is_title_fragment(text):
                metadata_elements.append(element)
                continue

            if self._is_diagram_label(text):
                metadata_elements.append(element)

        return metadata_elements

    def filter_excluded(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return special/non-retrievable elements such as
        figures, tables, diagrams, references and code.
        """

        return [
            element
            for element in elements
            if element.element_type
            in self.NON_RETRIEVABLE_TYPES
        ]

    def filter_for_semantic_chunking(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return clean elements suitable for semantic chunking.
        """

        return self.filter_retrievable(
            elements,
            metadata,
        )

    def separate_special_elements(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return figures, tables, diagrams, code,
        references, captions, headings and unknown elements.
        """

        return self.filter_excluded(
            elements
        )

    def _get_metadata_texts(
        self,
        metadata,
    ) -> set[str]:
        """
        Convert DocumentMetadata into a set of strings
        that should never enter semantic retrieval.
        """

        if metadata is None:
            return set()

        texts: set[str] = set()

        if metadata.title:
            texts.add(
                metadata.title.strip()
            )

        for author in metadata.authors:
            if author:
                texts.add(
                    author.strip()
                )

        for affiliation in metadata.affiliations:
            if affiliation:
                texts.add(
                    affiliation.strip()
                )

        for email in metadata.emails:
            if email:
                texts.add(
                    email.strip()
                )

        return texts

    def _is_structural_noise(
        self,
        text: str,
    ) -> bool:
        """
        Detect structural labels such as Abstract.
        """

        return bool(
            self.ABSTRACT_PATTERN.match(
                text
            )
        )

    def _is_page_number(
        self,
        text: str,
    ) -> bool:
        """
        Detect standalone page numbers.
        """

        return bool(
            self.PAGE_NUMBER_PATTERN.match(
                text
            )
        )

    def _is_arxiv_artifact(
        self,
        text: str,
    ) -> bool:
        """
        Detect arXiv header/footer artifacts.
        """

        return bool(
            self.ARXIV_PATTERN.match(
                text
            )
        )

    def _is_section_heading(
        self,
        text: str,
    ) -> bool:
        """
        Detect numbered section headings such as:

        1. Introduction
        2. Background
        3. Method and Experiments
        3.1. Experimental Setup
        """

        return bool(
            self.SECTION_HEADING_PATTERN.match(
                text
            )
        )

    def _is_title_fragment(
        self,
        text: str,
    ) -> bool:
        """
        Detect title fragments extracted as separate
        PDF blocks.
        """

        return bool(
            self.TITLE_FRAGMENT_PATTERN.match(
                text.strip()
            )
        )

    def _is_diagram_label(
        self,
        text: str,
    ) -> bool:
        """
        Detect short labels that commonly belong to
        diagrams rather than semantic document prose.
        """

        normalized = " ".join(
            text.strip().lower().split()
        )

        if not normalized:
            return False

        if normalized in self.DIAGRAM_LABELS:
            return True

        if normalized == "✕ n":
            return True

        # Very short labels are generally not useful
        # as independent semantic retrieval units.
        if len(normalized) <= 5:
            return True

        return False