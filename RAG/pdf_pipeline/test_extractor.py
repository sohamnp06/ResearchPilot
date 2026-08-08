from pathlib import Path

from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:
    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    pages = extractor.extract(pdf_path)

    total_blocks = sum(
        len(page.blocks)
        for page in pages
    )

    print(f"Pages: {len(pages)}")
    print(f"Total blocks: {total_blocks}")

    for page in pages[:1]:
        print()
        print(f"Page {page.page_number}")
        print(
            f"Dimensions: "
            f"{page.width:.2f} x {page.height:.2f}"
        )

        for block in page.blocks[:10]:
            print()
            print(
                f"Block {block.block_number}"
            )
            print("Text:", block.text)
            print("BBox:", block.bbox)

            for span in block.spans[:3]:
                print(
                    f"  Span: {span.text!r} "
                    f"| Font: {span.font} "
                    f"| Size: {span.font_size}"
                )


if __name__ == "__main__":
    main()