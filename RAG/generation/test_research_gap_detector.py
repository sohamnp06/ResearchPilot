from __future__ import annotations

import json

from RAG.generation.llm_generator import (
    LLMGenerator,
)

from RAG.generation.research_gap_detector import (
    ResearchGapDetector,
)


def main() -> None:

    print(
        "Testing Research Gap Detector..."
    )

    llm_generator = LLMGenerator()

    detector = ResearchGapDetector(
        llm_generator
    )

    context = """
[Source: chunk_00002 | Section: 2. Background | Page: 2]
However, it is not clear how the different parts of ViT
or its many variants contribute to the final performance
of each of these models.

[Source: chunk_00004 | Section: 3.2. Experimental Setup | Page: 2]
We train three models, corresponding to the ViT/DeiT tiny,
base, and large networks, on ImageNet using the setup from
DeiT. Notably, we use exactly the same hyperparameters as
DeiT for all models, which means that our performance could
likely be improved with hyperparameter tuning.

[Source: chunk_00007 | Section: 3.5. Discussion | Page: 3]
The above experiments demonstrate that it is possible to
train reasonably strong transformer-style image classifiers
without attention layers.

These results indicate that the strong performance of ViT
may be attributable more to its patch embeddings and training
procedure than to the design of the attention layer.

[Source: chunk_00008 | Section: 3.6. Conclusion | Page: 3]
Future work in this direction could attempt to better
understand the contributions of other pieces of the transformer
architecture, such as the normalization layer or initialization
scheme.
""".strip()

    print()
    print(
        "=" * 80
    )
    print(
        "DETECTING RESEARCH GAPS"
    )
    print(
        "=" * 80
    )

    result = detector.detect(
        context
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
        "RESEARCH GAP DETECTOR TEST PASSED"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()