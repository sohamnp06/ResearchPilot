from __future__ import annotations

import json

from RAG.generation.llm_generator import (
    LLMGenerator,
)

from RAG.generation.citation_verifier import (
    CitationVerifier,
)


def main() -> None:

    print(
        "Testing Citation Verifier..."
    )

    llm_generator = LLMGenerator()

    verifier = CitationVerifier(
        llm_generator
    )

    answer = (
        "The feed-forward-only version of "
        "ViT/DeiT-base achieved 74.9% top-1 "
        "accuracy on ImageNet."
    )

    context = """
[Source: chunk_00005 | Section: 3.3. Results | Pages: 2-3]
The feed-forward-only version of ViT/DeiT-base achieves
74.9% top-1 accuracy on ImageNet.

[Source: chunk_00007 | Section: 3.5. Discussion | Page: 3]
The experiments demonstrate that it is possible to train
reasonably strong transformer-style image classifiers
without attention layers.
""".strip()

    print()
    print(
        "=" * 80
    )
    print(
        "VERIFYING ANSWER"
    )
    print(
        "=" * 80
    )

    print()
    print(
        f"Answer: {answer}"
    )

    result = verifier.verify(
        answer=answer,
        context=context,
    )

    print()
    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print()
    print(
        "=" * 80
    )
    print(
        "CITATION VERIFIER TEST PASSED"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()