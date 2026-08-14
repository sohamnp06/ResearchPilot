from __future__ import annotations

import numpy as np

from RAG.retrieval.faiss_store import (
    FAISSStore,
)


def main() -> None:

    print("Testing FAISS store...")

    dimension = 4

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.8, 0.2, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    chunks = [
        {
            "chunk_id": "chunk_00000",
            "text": "Vision transformers use attention.",
            "section": "Introduction",
            "page_start": 1,
            "page_end": 1,
        },
        {
            "chunk_id": "chunk_00001",
            "text": "Feed-forward networks process features.",
            "section": "Background",
            "page_start": 2,
            "page_end": 2,
        },
        {
            "chunk_id": "chunk_00002",
            "text": "Vision transformers can work without attention.",
            "section": "Method",
            "page_start": 2,
            "page_end": 3,
        },
    ]

    # Convert dictionaries into simple objects
    # compatible with FAISSStore.
    from types import SimpleNamespace

    chunk_objects = [
        SimpleNamespace(**chunk)
        for chunk in chunks
    ]

    store = FAISSStore(
        dimension=dimension
    )

    store.add(
        embeddings,
        chunk_objects,
    )

    print(
        f"Vectors indexed: {store.size()}"
    )

    query = np.array(
        [0.9, 0.1, 0.0, 0.0],
        dtype=np.float32,
    )

    results = store.search(
        query,
        top_k=3,
    )

    print()
    print("=" * 80)
    print("SEARCH RESULTS")
    print("=" * 80)

    for result in results:

        print()
        print(
            f"Chunk ID: {result.chunk_id}"
        )

        print(
            f"Score: {result.score:.4f}"
        )

        print(
            f"Section: {result.section}"
        )

        print(
            f"Pages: "
            f"{result.page_start}-"
            f"{result.page_end}"
        )

        print(
            f"Text: {result.text}"
        )

        print("-" * 80)


if __name__ == "__main__":
    main()