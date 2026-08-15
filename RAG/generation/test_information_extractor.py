from __future__ import annotations

import json

from RAG.generation.llm_generator import (
    LLMGenerator,
)

from RAG.generation.information_extractor import (
    InformationExtractor,
)


def main() -> None:

    print(
        "Testing Information Extractor..."
    )

    llm_generator = LLMGenerator()

    extractor = InformationExtractor(
        llm_generator
    )

    context = """
[Source: chunk_00004 | Section: 3.2. Experimental Setup | Pages: 2-2]
We train three models, corresponding to the ViT/DeiT tiny,
base, and large networks, on ImageNet using the setup from
DeiT. The tiny and base networks have patch size 16, while
the large network has patch size 32. Training and evaluation
is performed at resolution 224px.

[Source: chunk_00005 | Section: 3.3. Results | Pages: 2-3]
The feed-forward-only version of ViT/DeiT-base achieves
74.9% top-1 accuracy on ImageNet.

[Source: chunk_00006 | Section: 3.4. Do You Even Need Feed-Forward Layers? | Page: 3]
A model with only attention layers achieved 28.2% top-1
accuracy at 100 epochs.

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
        "EXTRACTING INFORMATION"
    )
    print(
        "=" * 80
    )

    result = extractor.extract(
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
        "INFORMATION EXTRACTOR TEST PASSED"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()