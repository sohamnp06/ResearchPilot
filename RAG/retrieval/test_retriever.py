from __future__ import annotations

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

from RAG.chunking.sentence_splitter import (
    SentenceSplitter,
)

from RAG.chunking.paper_sentence_builder import (
    PaperSentenceBuilder,
)

from RAG.chunking.chunk_generator import (
    ChunkGenerator,
)

from RAG.embedding.embed import (
    EmbeddingModel,
)

from RAG.retrieval.retriever import (
    Retriever,
)


PDF_PATH = Path(
    "data/papers/2105.02723v1.pdf"
)


def main() -> None:

    print("Loading research paper...")

    # ==================================================
    # 1. PDF EXTRACTION
    # ==================================================

    extractor = PDFExtractor()

    pages = extractor.extract(
        PDF_PATH
    )

    print(
        f"Pages loaded: {len(pages)}"
    )

    # ==================================================
    # 2. METADATA DETECTION
    # ==================================================

    metadata_detector = (
        MetadataDetector()
    )

    metadata = (
        metadata_detector.detect(
            pages
        )
    )

    print(
        f"Title: {metadata.title}"
    )

    # ==================================================
    # 3. HEADING + SECTION DETECTION
    # ==================================================

    heading_detector = (
        HeadingDetector()
    )

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

    # ==================================================
    # 4. SENTENCE SPLITTING
    # ==================================================

    sentence_splitter = (
        SentenceSplitter()
    )

    sentence_builder = (
        PaperSentenceBuilder(
            sentence_splitter
        )
    )

    sentences = (
        sentence_builder.build(
            sections
        )
    )

    print(
        f"Sentences generated: "
        f"{len(sentences)}"
    )

    # ==================================================
    # 5. CHUNK GENERATION
    # ==================================================

    chunk_generator = (
        ChunkGenerator(
            max_characters=3000
        )
    )

    chunks = (
        chunk_generator.generate(
            sentences
        )
    )

    print(
        f"Chunks generated: "
        f"{len(chunks)}"
    )

    # ==================================================
    # 6. EMBEDDING MODEL
    # ==================================================

    print()
    print(
        "Loading embedding model..."
    )

    embedding_model = (
        EmbeddingModel()
    )

    print(
        f"Embedding dimension: "
        f"{embedding_model.dimension}"
    )

    # ==================================================
    # 7. RETRIEVER
    # ==================================================

    retriever = Retriever(
        embedding_model
    )

    # ==================================================
    # 8. INDEX REAL DOCUMENT CHUNKS
    # ==================================================

    print()
    print(
        "Indexing document chunks..."
    )

    retriever.index_chunks(
        chunks
    )

    print(
        f"Chunks indexed: "
        f"{retriever.size()}"
    )

    # ==================================================
    # 9. SEMANTIC SEARCH
    # ==================================================

    queries = [
        (
            "Why is attention important "
            "in vision transformers?"
        ),
        (
            "How well does the "
            "feed-forward-only model perform?"
        ),
        (
            "What experiments were "
            "conducted on ImageNet?"
        ),
    ]

    for query in queries:

        print()
        print("=" * 80)

        print(
            f"QUERY: {query}"
        )

        print("=" * 80)

        results = retriever.search(
            query=query,
            top_k=3,
        )

        for result in results:

            print()

            print(
                f"Chunk ID: "
                f"{result.chunk_id}"
            )

            print(
                f"Score: "
                f"{result.score:.4f}"
            )

            print(
                f"Section: "
                f"{result.section}"
            )

            print(
                f"Pages: "
                f"{result.page_start}-"
                f"{result.page_end}"
            )

            print(
                f"Text: "
                f"{result.text[:500]}"
            )

            print("-" * 80)


if __name__ == "__main__":
    main()