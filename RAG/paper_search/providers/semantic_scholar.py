from typing import List

import httpx

from settings import settings
from paper_search.exceptions import ProviderError
from paper_search.models import Author, Paper
from paper_search.providers.base_provider import BaseProvider


class SemanticScholarProvider(BaseProvider):
    """
    Semantic Scholar API Provider.
    """

    def __init__(self):
        self.base_url = settings.SEMANTIC_SCHOLAR_API

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Paper]:

        url = f"{self.base_url}/paper/search"

        params = {
            "query": query,
            "limit": limit,
            "fields": (
                "paperId,"
                "title,"
                "abstract,"
                "authors,"
                "year,"
                "citationCount,"
                "openAccessPdf"
            ),
        }

        try:

            async with httpx.AsyncClient(timeout=30) as client:

                response = await client.get(
                    url,
                    params=params,
                )

                response.raise_for_status()

        except httpx.HTTPError as e:
            raise ProviderError(
                f"Semantic Scholar API Error: {e}"
            ) from e

        papers = []

        data = response.json().get("data", [])

        for item in data:

            pdf = item.get("openAccessPdf")

            papers.append(
                Paper(
                    paper_id=item.get("paperId", ""),
                    title=item.get("title", ""),
                    abstract=item.get("abstract"),
                    authors=[
                        Author(name=author["name"])
                        for author in item.get("authors", [])
                    ],
                    year=item.get("year"),
                    citation_count=item.get("citationCount"),
                    pdf_url=pdf["url"] if pdf else None,
                    source="Semantic Scholar",
                )
            )

        return papers