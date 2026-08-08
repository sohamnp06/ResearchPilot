from typing import List

import httpx

from RAG.settings import settings
from RAG.paper_search.exceptions import ProviderError
from RAG.paper_search.models import Author, Paper
from RAG.paper_search.providers.base_provider import BaseProvider


class SemanticScholarProvider(BaseProvider):
    """
    Provider for searching papers through the
    Semantic Scholar Academic Graph API.
    """

    PROVIDER_NAME = "Semantic Scholar"

    def __init__(self) -> None:
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
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:

                response = await client.get(
                    url,
                    params=params,
                )

        except httpx.RequestError as exc:
            raise ProviderError(
                message=(
                    f"Unable to connect to "
                    f"{self.PROVIDER_NAME}: {exc}"
                ),
                provider=self.PROVIDER_NAME,
            ) from exc

        if response.status_code != 200:
            raise ProviderError(
                message=(
                    f"{self.PROVIDER_NAME} returned "
                    f"HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                ),
                provider=self.PROVIDER_NAME,
                status_code=response.status_code,
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderError(
                message=(
                    f"{self.PROVIDER_NAME} returned "
                    "invalid JSON."
                ),
                provider=self.PROVIDER_NAME,
                status_code=response.status_code,
            ) from exc

        data = payload.get("data", [])

        papers: List[Paper] = []

        for item in data:
            pdf = item.get("openAccessPdf")

            authors = [
                Author(name=author["name"])
                for author in item.get("authors", [])
                if author.get("name")
            ]

            papers.append(
                Paper(
                    paper_id=item.get("paperId", ""),
                    title=item.get("title", ""),
                    abstract=item.get("abstract"),
                    authors=authors,
                    year=item.get("year"),
                    citation_count=item.get("citationCount"),
                    pdf_url=pdf.get("url") if pdf else None,
                    source=self.PROVIDER_NAME,
                )
            )

        return papers