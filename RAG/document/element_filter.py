from __future__ import annotations

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class ElementFilter:
    """
    Filters document elements according to their role
    in the retrieval pipeline.
    """

    RETRIEVABLE_TYPES = {
        ElementType.PARAGRAPH,
    }

    NON_RETRIEVABLE_TYPES = {
        ElementType.FIGURE,
        ElementType.TABLE,
        ElementType.CODE,
        ElementType.REFERENCE,
        ElementType.UNKNOWN,
    }

    def filter_for_semantic_chunking(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return only normal paragraph elements for
        semantic chunking.
        """

        return [
            element
            for element in elements
            if element.element_type
            in self.RETRIEVABLE_TYPES
        ]

    def separate_special_elements(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return figures, tables, code, references,
        and other non-paragraph elements.
        """

        return [
            element
            for element in elements
            if element.element_type
            in self.NON_RETRIEVABLE_TYPES
        ]