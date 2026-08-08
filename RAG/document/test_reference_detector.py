from pathlib import Path

from RAG.document.reference_detector import (
    ReferenceDetector,
)
from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:

    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    pages = extractor.extract(
        pdf_path
    )

    detector = ReferenceDetector()

    references = detector.detect(
        pages
    )

    print(
        f"Detected references: "
        f"{len(references)}"
    )

    for reference in references[:10]:

        print()
        print(
            f"[{reference.index}] "
            f"Page={reference.page}"
        )

        print(
            reference.text
        )


if __name__ == "__main__":
    main()