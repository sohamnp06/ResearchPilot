from __future__ import annotations

import json

from RAG.generation.llm_generator import (
    LLMGenerator,
)

from RAG.generation.paper_comparator import (
    PaperComparator,
)


def main() -> None:

    print(
        "Testing Paper Comparator..."
    )

    llm_generator = LLMGenerator()

    comparator = PaperComparator(
        llm_generator
    )

    paper_a_context = """
Paper A

Objective:
Investigate whether attention is necessary
for strong vision transformer performance.

Methodology:
The attention layer is replaced with feed-forward
layers over the patch dimension.

Model:
ViT/DeiT-base.

Dataset:
ImageNet.

Metric:
Top-1 accuracy.

Result:
74.9% top-1 accuracy.

Experimental setting:
224px resolution and patch size 16.

Research finding:
Transformer-style image classifiers can perform
strongly without attention layers.
""".strip()

    paper_b_context = """
Paper B

Objective:
Evaluate the contribution of attention layers
to transformer-style image classification.

Methodology:
The model retains attention layers but modifies
the feed-forward component.

Model:
ViT-base.

Dataset:
ImageNet.

Metric:
Top-1 accuracy.

Result:
77.9% top-1 accuracy.

Experimental setting:
224px resolution and patch size 16.

Research finding:
Attention-based vision transformers achieve
strong image classification performance.
""".strip()

    print()
    print(
        "=" * 80
    )
    print(
        "COMPARING PAPERS"
    )
    print(
        "=" * 80
    )

    result = comparator.compare(
        paper_a_context=paper_a_context,
        paper_b_context=paper_b_context,
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
        "PAPER COMPARATOR TEST PASSED"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()