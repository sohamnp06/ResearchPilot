from __future__ import annotations

from RAG.document.elements import (
    DocumentElement,
)

from RAG.document.layout_classifier import (
    LayoutClassifier,
)


class DocumentElementBuilder:
    """
    Converts extracted PDF TextBlocks into classified
    DocumentElements.

    The builder also propagates table classification
    from table captions to the individual PDF blocks
    belonging to the table region.
    """

    def __init__(
        self,
        classifier: LayoutClassifier | None = None,
    ) -> None:

        self.classifier = (
            classifier
            or LayoutClassifier()
        )

    def build(
        self,
        pages: list,
    ) -> list[DocumentElement]:

        elements: list[DocumentElement] = []

        for page in pages:

            # --------------------------------------------------
            # Detect table regions before classifying individual
            # blocks.
            # --------------------------------------------------

            table_blocks = (
                self.classifier.detect_table_blocks(
                    page.blocks
                )
            )

            for block in page.blocks:

                forced_type = None

                if (
                    block.block_number
                    in table_blocks
                ):
                    forced_type = (
                        self._table_element_type()
                    )

                element = (
                    self.classifier.classify(
                        text=block.text,
                        page=page.page_number,
                        block_number=block.block_number,
                        bbox=block.bbox,
                        forced_type=forced_type,
                    )
                )

                if not element.text:
                    continue

                elements.append(element)

        return elements

    @staticmethod
    def _table_element_type():
        """
        Resolve ElementType.TABLE without changing the
        existing classifier API.
        """

        from RAG.document.elements import (
            ElementType,
        )

        return ElementType.TABLE