from RAG.embedding.embed import EmbeddingModel


def main() -> None:

    print(
        "Loading embedding model..."
    )

    model = EmbeddingModel()

    print(
        f"Model: {model.model_name}"
    )

    print(
        f"Embedding dimension: "
        f"{model.dimension}"
    )

    texts = [
        (
            "Vision transformers use "
            "attention mechanisms for image "
            "classification."
        ),
        (
            "The experiment replaces the "
            "attention layer with a "
            "feed-forward layer."
        ),
        (
            "The model was evaluated on "
            "ImageNet."
        ),
    ]

    print()
    print(
        "Generating embeddings..."
    )

    result = model.encode(
        texts
    )

    print()
    print(
        f"Number of texts: "
        f"{len(result.texts)}"
    )

    print(
        f"Embedding shape: "
        f"{result.embeddings.shape}"
    )

    print()
    print(
        "First embedding preview:"
    )

    print(
        result.embeddings[0][:10]
    )


if __name__ == "__main__":
    main()