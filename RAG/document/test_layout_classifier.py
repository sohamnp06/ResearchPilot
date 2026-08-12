from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor
from RAG.document.layout_classifier import (
    LayoutClassifier,
)


PDF_PATH = Path(
    "data/papers/2105.02723v1.pdf"
)


def main() -> None:

    print(
        "Loading PDF..."
    )

    extractor = PDFExtractor()

    pages = extractor.extract(
        PDF_PATH
    )

    classifier = LayoutClassifier()

    counts = {}

    print()
    print("=" * 80)

    for page in pages:

        for block in page.blocks:

            element = classifier.classify(
                text=block.text,
                page=page.page_number,
                block_number=block.block_number,
                bbox=block.bbox,
            )

            element_type = (
                element.element_type.value
            )

            counts[element_type] = (
                counts.get(
                    element_type,
                    0,
                )
                + 1
            )

            if (
                element.element_type.value
                != "paragraph"
            ):

                print()
                print(
                    f"Page: {element.page}"
                )

                print(
                    f"Block: "
                    f"{element.block_number}"
                )

                print(
                    f"Type: "
                    f"{element.element_type.value}"
                )

                print(
                    f"Text: "
                    f"{element.text[:300]}"
                )

                print("-" * 80)

    print()
    print("=" * 80)

    print(
        "Element counts:"
    )

    for element_type, count in sorted(
        counts.items()
    ):

        print(
            f"{element_type}: {count}"
        )


if __name__ == "__main__":
    main()