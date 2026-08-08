from pathlib import Path

from RAG.document.heading_detector import HeadingDetector
from RAG.document.metadata import MetadataDetector
from RAG.document.section_detector import SectionDetector
from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:

    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    pages = extractor.extract(
        pdf_path
    )

    metadata_detector = MetadataDetector()

    metadata = metadata_detector.detect(
        pages
    )

    heading_detector = HeadingDetector()

    section_detector = SectionDetector()

    sections = section_detector.detect(
        pages=pages,
        heading_detector=heading_detector,
        metadata=metadata,
    )

    print(
        f"Detected sections: {len(sections)}"
    )

    for section in sections:

        indentation = "    " * (
            section.level - 1
        )

        print(
            f"{indentation}"
            f"[L{section.level}] "
            f"{section.title}"
            f" | Page {section.page}"
            f" | Blocks {len(section.blocks)}"
        )


if __name__ == "__main__":
    main()