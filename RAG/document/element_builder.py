from __future__ import annotations

from RAG.document.elements import DocumentElement
from RAG.document.layout_classifier import LayoutClassifier


class DocumentElementBuilder:
    """
    Converts extracted PDF TextBlocks into classified
    DocumentElements.
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
        """
        Convert every extracted TextBlock into a
        DocumentElement using LayoutClassifier.
        """

        elements: list[DocumentElement] = []

        for page in pages:

            for block in page.blocks:

                element = self.classifier.classify(
                    text=block.text,
                    page=page.page_number,
                    block_number=block.block_number,
                    bbox=block.bbox,
                )

                # Ignore empty blocks.
                if not element.text:
                    continue

                elements.append(element)

        return elements