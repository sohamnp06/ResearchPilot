from __future__ import annotations

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class ElementFilter:
    """
    Filters document elements according to their role
    in the retrieval pipeline.

    Paragraph elements are suitable for semantic retrieval.

    Figures, tables, diagrams, code, references,
    captions, and unknown elements are excluded
    from the normal retrieval pipeline.
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
    }

    def filter_retrievable(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return elements suitable for semantic retrieval.

        Metadata is optionally accepted so that callers using
        document-level metadata can exclude those elements
        from retrieval as well.
        """

        metadata_texts = self._get_metadata_texts(
            metadata
        )

        return [
            element
            for element in elements
            if (
                element.element_type
                in self.RETRIEVABLE_TYPES
                and element.text.strip()
                not in metadata_texts
            )
        ]

    def filter_excluded(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Return elements that should be excluded from
        the normal semantic retrieval pipeline.
        """

        return [
            element
            for element in elements
            if element.element_type
            in self.NON_RETRIEVABLE_TYPES
        ]

    def filter_metadata(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return elements whose text corresponds to
        document metadata.

        This does not require a METADATA ElementType.
        """

        if metadata is None:
            return []

        metadata_texts = self._get_metadata_texts(
            metadata
        )

        return [
            element
            for element in elements
            if element.text.strip()
            in metadata_texts
        ]

    def filter_for_semantic_chunking(
        self,
        elements: list[DocumentElement],
        metadata=None,
    ) -> list[DocumentElement]:
        """
        Return only elements suitable for semantic chunking.
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
        references, captions, and unknown elements.
        """

        return self.filter_excluded(
            elements
        )

    def _get_metadata_texts(
        self,
        metadata,
    ) -> set[str]:
        """
        Convert DocumentMetadata into a set of text
        values that should not enter semantic retrieval.
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