from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor
from RAG.document.element_builder import (
    DocumentElementBuilder,
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

    builder = DocumentElementBuilder()

    elements = builder.build(
        pages
    )

    print()
    print(
        f"Total document elements: "
        f"{len(elements)}"
    )

    counts = {}

    for element in elements:

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

    print()
    print("Element counts:")

    for element_type, count in sorted(
        counts.items()
    ):

        print(
            f"{element_type}: {count}"
        )

    print()
    print("=" * 80)

    print(
        "Special elements:"
    )

    for element in elements:

        if (
            element.element_type.value
            != "paragraph"
        ):

            print()
            print(
                f"Type: "
                f"{element.element_type.value}"
            )

            print(
                f"Page: "
                f"{element.page}"
            )

            print(
                f"Block: "
                f"{element.block_number}"
            )

            print(
                f"Text: "
                f"{element.text[:250]}"
            )

            print("-" * 80)


if __name__ == "__main__":
    main()