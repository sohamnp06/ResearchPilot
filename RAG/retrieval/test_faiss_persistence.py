from __future__ import annotations

from pathlib import Path

from RAG.embedding.embed import (
    EmbeddingModel,
)

from RAG.retrieval.retriever import (
    Retriever,
)


SAVE_DIRECTORY = Path(
    "data/faiss_index"
)


def main() -> None:

    print(
        "Testing FAISS persistence..."
    )

    # ==================================================
    # 1. LOAD EMBEDDING MODEL
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
    # 2. CREATE TEST CHUNKS
    # ==================================================

    chunks = [
        {
            "chunk_id": "chunk_00000",
            "text": (
                "Vision transformers use "
                "attention mechanisms to process "
                "image patches."
            ),
            "section": "Introduction",
            "page_start": 1,
            "page_end": 1,
        },
        {
            "chunk_id": "chunk_00001",
            "text": (
                "Feed-forward networks process "
                "features across the representation."
            ),
            "section": "Background",
            "page_start": 2,
            "page_end": 2,
        },
        {
            "chunk_id": "chunk_00002",
            "text": (
                "Vision transformers can achieve "
                "strong performance without attention."
            ),
            "section": "Results",
            "page_start": 3,
            "page_end": 3,
        },
    ]

    # ==================================================
    # 3. CREATE RETRIEVER
    # ==================================================

    retriever = Retriever(
        embedding_model
    )

    # ==================================================
    # 4. INDEX CHUNKS
    # ==================================================

    print()
    print(
        "Indexing test chunks..."
    )

    retriever.index_chunks(
        chunks
    )

    print(
        f"Vectors indexed: "
        f"{retriever.size()}"
    )

    # ==================================================
    # 5. SAVE INDEX
    # ==================================================

    print()
    print(
        "Saving FAISS index..."
    )

    retriever.save(
        SAVE_DIRECTORY
    )

    print(
        f"Saved to: "
        f"{SAVE_DIRECTORY}"
    )

    # ==================================================
    # 6. CREATE NEW RETRIEVER
    # ==================================================

    print()
    print(
        "Creating new retriever..."
    )

    loaded_retriever = Retriever(
        embedding_model
    )

    # ==================================================
    # 7. LOAD INDEX
    # ==================================================

    print(
        "Loading saved index..."
    )

    loaded_retriever.load(
        SAVE_DIRECTORY
    )

    print(
        f"Vectors loaded: "
        f"{loaded_retriever.size()}"
    )

    # ==================================================
    # 8. SEARCH LOADED INDEX
    # ==================================================

    query = (
        "Why is attention useful "
        "in vision transformers?"
    )

    print()
    print("=" * 80)

    print(
        f"QUERY: {query}"
    )

    print("=" * 80)

    results = loaded_retriever.search(
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
            f"{result.text}"
        )

        print("-" * 80)

    # ==================================================
    # 9. VALIDATE PERSISTENCE
    # ==================================================

    assert (
        retriever.size()
        == loaded_retriever.size()
    ), (
        "Loaded index size does not match "
        "original index size."
    )

    assert (
        loaded_retriever.size()
        == len(chunks)
    ), (
        "Loaded index does not contain "
        "all indexed chunks."
    )

    assert (
        len(results) == 3
    ), (
        "Expected 3 search results."
    )

    result_ids = {
        result.chunk_id
        for result in results
    }

    expected_ids = {
        "chunk_00000",
        "chunk_00001",
        "chunk_00002",
    }

    assert (
        result_ids == expected_ids
    ), (
        "Loaded FAISS index did not "
        "return all expected chunk IDs."
    )

    for result in results:

        assert result.text, (
            f"Missing text for "
            f"{result.chunk_id}"
        )

        assert result.section, (
            f"Missing section for "
            f"{result.chunk_id}"
        )

        assert result.page_start is not None, (
            f"Missing page_start for "
            f"{result.chunk_id}"
        )

        assert result.page_end is not None, (
            f"Missing page_end for "
            f"{result.chunk_id}"
        )

    print()
    print("=" * 80)
    print(
        "FAISS persistence test PASSED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()