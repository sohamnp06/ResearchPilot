from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:
    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    blocks = extractor.extract(pdf_path)

    print(f"Extracted blocks: {len(blocks)}")

    for block in blocks[:10]:
        print()
        print("Page:", block["page"])
        print("Block:", block["block"])
        print("Text:", block["text"])
        print("BBox:", block["bbox"])
        print("Font:", block["font"])
        print("Font size:", block["font_size"])


if __name__ == "__main__":
    main()