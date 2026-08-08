from pathlib import Path

from RAG.document.metadata import MetadataDetector
from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:

    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    pages = extractor.extract(
        pdf_path
    )

    detector = MetadataDetector()

    metadata = detector.detect(
        pages
    )

    print("TITLE:")
    print(metadata.title)

    print()
    print("AUTHORS:")
    print(metadata.authors)

    print()
    print("AFFILIATIONS:")
    print(metadata.affiliations)

    print()
    print("EMAILS:")
    print(metadata.emails)

    print()
    print("ABSTRACT:")
    print(metadata.abstract)


if __name__ == "__main__":
    main()