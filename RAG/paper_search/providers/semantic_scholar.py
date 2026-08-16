from typing import List, Optional
import asyncio

import httpx

from RAG.settings import settings
from RAG.paper_search.exceptions import ProviderError
from RAG.paper_search.models import Author, Paper
from RAG.paper_search.providers.base_provider import BaseProvider


class SemanticScholarProvider(BaseProvider):
    """
    Provider for searching papers through the
    Semantic Scholar Academic Graph API.

    Uses the SEMANTIC_SCHOLAR_API_KEY from settings.
    Implements retry with exponential backoff for 429 responses.
    """

    PROVIDER_NAME = "Semantic Scholar"
    MAX_RETRIES = 3
    RETRY_BACKOFF = [1.0, 2.0, 4.0]  # seconds

    def __init__(self) -> None:
        self.base_url = settings.SEMANTIC_SCHOLAR_API
        self._api_key: Optional[str] = settings.SEMANTIC_SCHOLAR_API_KEY

    def _build_headers(self) -> dict:
        headers = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key
        return headers

    async def search(
        self,
        query: str,
        limit: int = 10,
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
                "openAccessPdf,"
                "externalIds,"
                "url"
            ),
        }

        headers = self._build_headers()
        last_error: Optional[Exception] = None

        for attempt, backoff in enumerate(self.RETRY_BACKOFF):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        url,
                        params=params,
                        headers=headers,
                    )

            except httpx.RequestError as exc:
                raise ProviderError(
                    message=(
                        f"Unable to connect to "
                        f"{self.PROVIDER_NAME}: {exc}"
                    ),
                    provider=self.PROVIDER_NAME,
                ) from exc

            # Rate limit — retry with backoff
            if response.status_code == 429:
                if attempt < len(self.RETRY_BACKOFF) - 1:
                    await asyncio.sleep(backoff)
                    last_error = ProviderError(
                        message=f"{self.PROVIDER_NAME} rate limit hit (429).",
                        provider=self.PROVIDER_NAME,
                        status_code=429,
                    )
                    continue
                raise ProviderError(
                    message=(
                        f"{self.PROVIDER_NAME} rate limit exceeded. "
                        "Please try again later."
                    ),
                    provider=self.PROVIDER_NAME,
                    status_code=429,
                )

            # Auth errors — don't retry
            if response.status_code in (401, 403):
                raise ProviderError(
                    message=(
                        f"{self.PROVIDER_NAME} authentication failed "
                        f"(HTTP {response.status_code}). "
                        "Check SEMANTIC_SCHOLAR_API_KEY."
                    ),
                    provider=self.PROVIDER_NAME,
                    status_code=response.status_code,
                )

            # Not found
            if response.status_code == 404:
                return []

            # Server errors — retry
            if response.status_code >= 500:
                if attempt < len(self.RETRY_BACKOFF) - 1:
                    await asyncio.sleep(backoff)
                    last_error = ProviderError(
                        message=(
                            f"{self.PROVIDER_NAME} server error "
                            f"(HTTP {response.status_code})."
                        ),
                        provider=self.PROVIDER_NAME,
                        status_code=response.status_code,
                    )
                    continue
                raise ProviderError(
                    message=(
                        f"{self.PROVIDER_NAME} returned "
                        f"HTTP {response.status_code}: "
                        f"{response.text[:200]}"
                    ),
                    provider=self.PROVIDER_NAME,
                    status_code=response.status_code,
                )

            if response.status_code != 200:
                raise ProviderError(
                    message=(
                        f"{self.PROVIDER_NAME} returned "
                        f"HTTP {response.status_code}: "
                        f"{response.text[:200]}"
                    ),
                    provider=self.PROVIDER_NAME,
                    status_code=response.status_code,
                )

            # Successful response
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

                # Try to get arXiv PDF as fallback when openAccessPdf is absent
                pdf_url = pdf.get("url") if pdf else None
                if not pdf_url:
                    external_ids = item.get("externalIds") or {}
                    arxiv_id = external_ids.get("ArXiv")
                    if arxiv_id:
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

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
                        pdf_url=pdf_url,
                        source=self.PROVIDER_NAME,
                    )
                )

            return papers

        # All retries exhausted
        if last_error:
            raise last_error

        return []