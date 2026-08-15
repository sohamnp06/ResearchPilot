from __future__ import annotations

from RAG.generation.llm_generator import (
    LLMGenerator,
)


def main() -> None:

    print(
        "Testing Ollama LLM Generator..."
    )

    generator = LLMGenerator()

    query = (
        "How well does the feed-forward-only "
        "model perform?"
    )

    context = """
[Source: chunk_00005 | Section: 3.3. Results | Pages: 2-3 | Score: 0.8421]
The feed-forward-only version of ViT/DeiT-base achieves
74.9% top-1 accuracy on ImageNet.

[Source: chunk_00007 | Section: 3.5. Discussion | Pages: 3 | Score: 0.7312]
The experiments demonstrate that transformer-style image
classifiers can perform reasonably well without attention layers.
""".strip()

    print()
    print(
        "=" * 80
    )
    print(
        "QUERY"
    )
    print(
        "=" * 80
    )

    print(query)

    print()
    print(
        "Generating answer..."
    )

    result = generator.generate(
        query=query,
        context=context,
    )

    print()
    print(
        "=" * 80
    )
    print(
        "LLM ANSWER"
    )
    print(
        "=" * 80
    )

    print()
    print(
        result.answer
    )

    print()
    print(
        f"Model: {result.model}"
    )

    print()
    print(
        "=" * 80
    )
    print(
        "OLLAMA LLM GENERATOR TEST PASSED"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()