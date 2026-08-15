from __future__ import annotations

from RAG.generation.context_assembler import (
    ContextAssembler,
)
from RAG.retrieval.faiss_store import (
    SearchResult,
)


def main() -> None:

    print(
        "Testing Context Assembler..."
    )

    # ==================================================
    # TEST SEARCH RESULTS
    # ==================================================

    results = [
        SearchResult(
            chunk_id="chunk_00005",
            score=0.8421,
            section="3.3. Results",
            page_start=2,
            page_end=3,
            text=(
                "The feed-forward-only version "
                "of ViT/DeiT-base achieves "
                "74.9% top-1 accuracy on "
                "ImageNet."
            ),
        ),
        SearchResult(
            chunk_id="chunk_00007",
            score=0.7312,
            section="3.5. Discussion",
            page_start=3,
            page_end=3,
            text=(
                "The experiments demonstrate "
                "that transformer-style image "
                "classifiers can perform "
                "reasonably well without "
                "attention layers."
            ),
        ),
        SearchResult(
            chunk_id="chunk_00008",
            score=0.6124,
            section="3.6. Conclusion",
            page_start=3,
            page_end=3,
            text=(
                "The report demonstrates that "
                "transformer-style networks "
                "without attention layers "
                "can make strong image "
                "classifiers."
            ),
        ),
    ]

    # ==================================================
    # CREATE ASSEMBLER
    # ==================================================

    assembler = ContextAssembler(
        max_context_characters=12000
    )

    # ==================================================
    # ASSEMBLE CONTEXT
    # ==================================================

    query = (
        "How well does the feed-forward-only "
        "model perform?"
    )

    context = assembler.assemble(
        query=query,
        results=results,
    )

    # ==================================================
    # DISPLAY RESULTS
    # ==================================================

    print()
    print("=" * 80)
    print("CONTEXT ASSEMBLY RESULTS")
    print("=" * 80)

    print()
    print(
        f"Query: {context.query}"
    )

    print(
        f"Context items: "
        f"{len(context.items)}"
    )

    print(
        f"Context characters: "
        f"{len(context.text)}"
    )

    print()
    print("=" * 80)
    print("ASSEMBLED CONTEXT")
    print("=" * 80)

    print()

    print(
        context.text
    )

    # ==================================================
    # VALIDATION
    # ==================================================

    assert len(
        context.items
    ) == 3

    assert (
        context.items[0].chunk_id
        == "chunk_00005"
    )

    assert (
        context.items[1].section
        == "3.5. Discussion"
    )

    assert (
        context.items[0].page_start
        == 2
    )

    assert (
        context.items[0].page_end
        == 3
    )

    assert (
        "74.9% top-1 accuracy"
        in context.text
    )

    assert (
        "chunk_00005"
        in context.text
    )

    assert (
        "3.3. Results"
        in context.text
    )

    assert (
        "Pages: 2-3"
        in context.text
    )

    print()
    print("=" * 80)
    print(
        "CONTEXT ASSEMBLER TEST PASSED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()