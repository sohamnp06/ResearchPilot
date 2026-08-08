import asyncio

from RAG.paper_search.cache import PaperCache
from RAG.paper_search.downloader import PaperDownloader
from RAG.paper_search.providers.arxiv import ArxivProvider
from RAG.paper_search.service import PaperSearchService


async def main() -> None:
    print("Searching for paper...")

    provider = ArxivProvider()

    search_service = PaperSearchService(
        providers=[provider]
    )

    papers = await search_service.search(
        query="Attention Is All You Need",
        limit=1,
    )

    if not papers:
        print("No papers found.")
        return

    paper = papers[0]

    print()
    print("Selected paper:")
    print(paper.title)
    print("PDF URL:", paper.pdf_url)

    cache = PaperCache()

    downloader = PaperDownloader(
        cache=cache
    )

    print()
    print("Downloading PDF...")

    pdf_path = await downloader.download(
        paper
    )

    print()
    print("PDF downloaded successfully.")
    print("Local path:", pdf_path)


if __name__ == "__main__":
    asyncio.run(main())