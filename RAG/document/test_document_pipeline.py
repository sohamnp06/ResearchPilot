from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor

from RAG.document.metadata import (
    MetadataDetector,
)

from RAG.document.heading_detector import (
    HeadingDetector,
)

from RAG.document.section_detector import (
    SectionDetector,
)

from RAG.document.element_builder import (
    DocumentElementBuilder,
)

from RAG.document.section_assigner import (
    SectionAssigner,
)


PDF_PATH = Path(
    "data/papers/2105.02723v1.pdf"
)


def main() -> None:

    print("Loading PDF...")

    extractor = PDFExtractor()

    pages = extractor.extract(
        PDF_PATH
    )

    print(
        f"Pages: {len(pages)}"
    )

    # -----------------------------------------
    # Metadata
    # -----------------------------------------

    metadata_detector = (
        MetadataDetector()
    )

    metadata = metadata_detector.detect(
        pages
    )

    # -----------------------------------------
    # Heading detection
    # -----------------------------------------

    heading_detector = (
        HeadingDetector()
    )

    # -----------------------------------------
    # Section detection
    # -----------------------------------------

    section_detector = (
        SectionDetector()
    )

    sections = section_detector.detect(
        pages=pages,
        heading_detector=heading_detector,
        metadata=metadata,
    )

    print(
        f"Sections: {len(sections)}"
    )

    # -----------------------------------------
    # Document elements
    # -----------------------------------------

    element_builder = (
        DocumentElementBuilder()
    )

    elements = element_builder.build(
        pages
    )

    print(
        f"Elements: {len(elements)}"
    )

    # -----------------------------------------
    # Section assignment
    # -----------------------------------------

    assigner = SectionAssigner()

    elements = assigner.assign(
        elements,
        sections,
    )

    print()
    print("=" * 80)
    print(
        "Paragraph section assignments"
    )
    print("=" * 80)

    paragraph_count = 0

    for element in elements:

        if (
            element.element_type.value
            != "paragraph"
        ):
            continue

        paragraph_count += 1

        print()
        print(
            f"Page: {element.page}"
        )

        print(
            f"Block: {element.block_number}"
        )

        print(
            f"Section: {element.section}"
        )

        print(
            f"Heading: {element.heading}"
        )

        print(
            f"BBox: {element.bbox}"
        )

        print(
            f"Text: {element.text[:250]}"
        )

        print("-" * 80)

        if paragraph_count >= 15:
            break


if __name__ == "__main__":
    main()