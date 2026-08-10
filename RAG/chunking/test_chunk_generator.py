from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor
from RAG.document.metadata import MetadataDetector
from RAG.document.heading_detector import HeadingDetector
from RAG.document.section_detector import SectionDetector

from RAG.chunking.sentence_splitter import (
    SentenceSplitter,
)

from RAG.chunking.paper_sentence_builder import (
    PaperSentenceBuilder,
)

from RAG.chunking.chunk_generator import (
    ChunkGenerator,
)


PDF_PATH = Path(
    "data/papers/2105.02723v1.pdf"
)


def main() -> None:

    print(
        "Loading research paper..."
    )

    extractor = PDFExtractor()

    pages = extractor.extract(
        PDF_PATH
    )

    print(
        f"Pages loaded: {len(pages)}"
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
        f"Sections detected: "
        f"{len(sections)}"
    )

    # -----------------------------------------
    # Sentence generation
    # -----------------------------------------

    splitter = SentenceSplitter()

    sentence_builder = (
        PaperSentenceBuilder(
            sentence_splitter=splitter
        )
    )

    sentences = sentence_builder.build(
        sections
    )

    print(
        f"Sentences generated: "
        f"{len(sentences)}"
    )

    # -----------------------------------------
    # Chunk generation
    # -----------------------------------------

    generator = ChunkGenerator(
        max_characters=3000
    )

    chunks = generator.generate(
        sentences
    )

    print(
        f"Chunks generated: "
        f"{len(chunks)}"
    )

    print()
    print("=" * 80)

    for chunk in chunks:

        print()
        print(
            f"Chunk ID: "
            f"{chunk.chunk_id}"
        )

        print(
            f"Section: "
            f"{chunk.section}"
        )

        print(
            f"Pages: "
            f"{chunk.page_start}"
            f"-"
            f"{chunk.page_end}"
        )

        print(
            f"Sentences: "
            f"{chunk.sentence_count}"
        )

        print(
            f"Characters: "
            f"{chunk.character_count}"
        )

        print(
            "Text:"
        )

        print(
            chunk.text[:500]
        )

        print("-" * 80)


if __name__ == "__main__":
    main()