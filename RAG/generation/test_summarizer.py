from __future__ import annotations

from RAG.generation.llm_generator import (
    LLMGenerator,
)

from RAG.generation.summarizer import (
    PaperSummarizer,
)


def main() -> None:

    print(
        "Testing Paper Summarizer..."
    )

    llm_generator = LLMGenerator()

    summarizer = PaperSummarizer(
        llm_generator
    )

    context = """
[Source: chunk_00000 | Section: 1. Introduction | Pages: 1-2]
The vision transformer architecture applies a series of
transformer blocks to a sequence of image patches. Each block
consists of a multi-head attention layer followed by a
feed-forward layer.

[Source: chunk_00005 | Section: 3.3. Results | Pages: 2-3]
The feed-forward-only version of ViT/DeiT-base achieves
74.9% top-1 accuracy on ImageNet.

[Source: chunk_00007 | Section: 3.5. Discussion | Page: 3]
The experiments demonstrate that it is possible to train
reasonably strong transformer-style image classifiers
without attention layers.

[Source: chunk_00008 | Section: 3.6. Conclusion | Page: 3]
Transformer-style networks without attention layers make
for surprisingly strong image classifiers.
""".strip()

    print()
    print(
        "=" * 80
    )
    print(
        "GENERATING SUMMARY"
    )
    print(
        "=" * 80
    )

    summary = summarizer.summarize(
        context
    )

    print()
    print(summary)

    print()
    print(
        "=" * 80
    )
    print(
        "PAPER SUMMARIZER TEST PASSED"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()