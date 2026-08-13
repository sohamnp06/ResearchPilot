from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor

from RAG.document.element_builder import (
    DocumentElementBuilder,
)

from RAG.document.element_filter import (
    ElementFilter,
)

from RAG.document.metadata import (
    MetadataDetector,
)


PDF_PATH = Path(
    "data/papers/2105.02723v1.pdf"
)


def main() -> None:

    print("Loading PDF...")

    # --------------------------------------------------
    # 1. Extract PDF pages
    # --------------------------------------------------

    extractor = PDFExtractor()

    pages = extractor.extract(
        PDF_PATH
    )

    print(
        f"Pages loaded: {len(pages)}"
    )

    # --------------------------------------------------
    # 2. Detect document metadata
    # --------------------------------------------------

    metadata_detector = MetadataDetector()

    metadata = metadata_detector.detect(
        pages
    )

    print()
    print("=" * 80)
    print("DOCUMENT METADATA")
    print("=" * 80)

    print(
        f"Title: {metadata.title}"
    )

    print(
        f"Authors: {metadata.authors}"
    )

    print(
        f"Affiliations: "
        f"{metadata.affiliations}"
    )

    print(
        f"Emails: {metadata.emails}"
    )

    # --------------------------------------------------
    # 3. Build document elements
    # --------------------------------------------------

    builder = DocumentElementBuilder()

    elements = builder.build(
        pages
    )

    # --------------------------------------------------
    # 4. Filter document elements
    # --------------------------------------------------

    element_filter = ElementFilter()

    retrievable = (
        element_filter.filter_retrievable(
            elements,
            metadata,
        )
    )

    metadata_elements = (
        element_filter.filter_metadata(
            elements
        )
    )

    excluded = (
        element_filter.filter_excluded(
            elements
        )
    )

    # --------------------------------------------------
    # 5. Display filter results
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("ELEMENT FILTER RESULTS")
    print("=" * 80)

    print(
        f"Total elements: "
        f"{len(elements)}"
    )

    print(
        f"Retrievable elements: "
        f"{len(retrievable)}"
    )

    print(
        f"Metadata elements: "
        f"{len(metadata_elements)}"
    )

    print(
        f"Excluded elements: "
        f"{len(excluded)}"
    )

    # --------------------------------------------------
    # 6. Display retrievable elements
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("RETRIEVABLE ELEMENTS")
    print("=" * 80)

    for element in retrievable[:15]:

        print()
        print(
            f"Page: {element.page}"
        )

        print(
            f"Block: "
            f"{element.block_number}"
        )

        print(
            f"Section: "
            f"{element.section}"
        )

        print(
            f"Heading: "
            f"{element.heading}"
        )

        print(
            f"Text: "
            f"{element.text[:300]}"
        )

        print("-" * 80)

    # --------------------------------------------------
    # 7. Display metadata elements
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("METADATA ELEMENTS")
    print("=" * 80)

    for element in metadata_elements:

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

    # --------------------------------------------------
    # 8. Display excluded element types
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("EXCLUDED ELEMENT TYPES")
    print("=" * 80)

    excluded_types = {}

    for element in excluded:

        element_type = (
            element.element_type.value
        )

        excluded_types[element_type] = (
            excluded_types.get(
                element_type,
                0,
            )
            + 1
        )

    for element_type, count in sorted(
        excluded_types.items()
    ):

        print(
            f"{element_type}: {count}"
        )

    # --------------------------------------------------
    # 9. Display metadata-filtered paragraphs
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("METADATA REMOVED FROM RETRIEVAL")
    print("=" * 80)

    metadata_texts = set()

    if metadata.title:
        metadata_texts.add(
            metadata.title.strip().lower()
        )

    for author in metadata.authors:
        metadata_texts.add(
            author.strip().lower()
        )

    for affiliation in metadata.affiliations:
        metadata_texts.add(
            affiliation.strip().lower()
        )

    for email in metadata.emails:
        metadata_texts.add(
            email.strip().lower()
        )

    metadata_texts.add("abstract")

    removed_count = 0

    for element in elements:

        normalized = (
            element.text.strip().lower()
        )

        if normalized in metadata_texts:

            print(
                f"Removed: "
                f"{element.text}"
            )

            removed_count += 1

    print()
    print(
        f"Metadata items excluded: "
        f"{removed_count}"
    )


if __name__ == "__main__":
    main()