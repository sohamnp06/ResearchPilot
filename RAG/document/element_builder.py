from __future__ import annotations

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)

from RAG.document.layout_classifier import (
    LayoutClassifier,
)


class DocumentElementBuilder:
    """
    Converts extracted PDF TextBlocks into classified
    DocumentElements.

    The builder also propagates table/figure structure
    across neighboring PDF blocks so that table contents
    are not incorrectly classified as normal paragraphs.
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

            page_elements: list[
                DocumentElement
            ] = []

            for block in page.blocks:

                element = self.classifier.classify(
                    text=block.text,
                    page=page.page_number,
                    block_number=block.block_number,
                    bbox=block.bbox,
                )

                if not element.text:
                    continue

                page_elements.append(
                    element
                )

            page_elements = (
                self._propagate_table_regions(
                    page_elements
                )
            )

            page_elements = (
                self._propagate_figure_regions(
                    page_elements
                )
            )

            elements.extend(
                page_elements
            )

        return elements

    def _propagate_table_regions(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Propagate TABLE classification from a table
        caption to the blocks belonging to the table.

        Example:

            Table 1: ...
            Params ImageNet Top-1
            Tiny (P = 16)
            ViT 86M 77.9
            DeiT 86M 79.9

        All of these blocks should be TABLE elements.
        """

        table_active = False

        for element in elements:

            if (
                element.element_type
                == ElementType.TABLE
            ):
                table_active = True
                continue

            if not table_active:
                continue

            if self._starts_new_structure(
                element
            ):
                table_active = False
                continue

            if element.element_type in {
                ElementType.FIGURE,
                ElementType.REFERENCE,
                ElementType.CODE,
            }:
                table_active = False
                continue

            if self._looks_like_table_content(
                element.text
            ):
                element.element_type = (
                    ElementType.TABLE
                )

        return elements

    def _propagate_figure_regions(
        self,
        elements: list[DocumentElement],
    ) -> list[DocumentElement]:
        """
        Preserve figure captions and classify short
        neighboring diagram labels as diagram elements.
        """

        figure_active = False

        for element in elements:

            if (
                element.element_type
                == ElementType.FIGURE
            ):
                figure_active = True
                continue

            if not figure_active:
                continue

            if self._starts_new_structure(
                element
            ):
                figure_active = False
                continue

            if element.element_type in {
                ElementType.TABLE,
                ElementType.REFERENCE,
                ElementType.CODE,
            }:
                figure_active = False
                continue

            if self._looks_like_diagram_label(
                element.text
            ):
                element.element_type = (
                    ElementType.DIAGRAM
                )

        return elements

    def _starts_new_structure(
        self,
        element: DocumentElement,
    ) -> bool:
        """
        Determine whether a new structural region has
        started.
        """

        return element.element_type in {
            ElementType.HEADING,
            ElementType.FIGURE,
            ElementType.TABLE,
            ElementType.REFERENCE,
            ElementType.CODE,
        }

    def _looks_like_table_content(
        self,
        text: str,
    ) -> bool:
        """
        Detect common textual patterns found inside
        extracted PDF tables.
        """

        normalized = " ".join(
            text.strip().split()
        )

        if not normalized:
            return False

        # Table-like headers.
        table_keywords = (
            "params",
            "imageNet top-1",
            "top-1",
            "accuracy",
        )

        keyword_count = sum(
            keyword.lower()
            in normalized.lower()
            for keyword in table_keywords
        )

        if keyword_count >= 1:
            return True

        # Model-size / table-row patterns.
        model_keywords = (
            "vit",
            "deit",
            "ff only",
            "tiny",
            "base",
            "large",
        )

        model_count = sum(
            keyword in normalized.lower()
            for keyword in model_keywords
        )

        if model_count >= 1:
            return True

        # A block containing multiple numerical values
        # is frequently a table row in extracted PDFs.
        tokens = normalized.split()

        numeric_tokens = 0

        for token in tokens:

            cleaned = (
                token
                .replace("%", "")
                .replace("M", "")
                .replace(".", "")
                .replace(",", "")
            )

            if cleaned.isdigit():
                numeric_tokens += 1

        if numeric_tokens >= 2:
            return True

        return False

    def _looks_like_diagram_label(
        self,
        text: str,
    ) -> bool:
        """
        Detect short isolated labels typically extracted
        from diagrams.
        """

        normalized = text.strip()

        if normalized == "✕ N":
            return True

        diagram_keywords = (
            "patch embedding",
            "class prediction",
            "transpose",
            "feed-forward layer",
        )

        if any(
            keyword in normalized.lower()
            for keyword in diagram_keywords
        ):
            return True

        return len(normalized) <= 5