import asyncio

from RAG.paper_search.providers.arxiv import ArxivProvider
from RAG.paper_search.service import PaperSearchService


async def main() -> None:
    print("Starting arXiv paper search...")
    print()

    provider = ArxivProvider()

    service = PaperSearchService(
        providers=[provider]
    )

    papers = await service.search(
        query="Attention Is All You Need",
        limit=5,
    )

    print(f"Found {len(papers)} papers.")

    for paper in papers:
        print()
        print("Title:", paper.title)
        print("Year:", paper.year)
        print(
            "Authors:",
            [author.name for author in paper.authors],
        )
        print("PDF:", paper.pdf_url)
        print("Source:", paper.source)


if __name__ == "__main__":
    asyncio.run(main())