from typing import List
from xml.etree import ElementTree

import httpx

from RAG.paper_search.exceptions import ProviderError
from RAG.paper_search.models import Author, Paper
from RAG.paper_search.providers.base_provider import BaseProvider
from RAG.settings import settings


class ArxivProvider(BaseProvider):
    """
    Provider for searching research papers through arXiv.
    """

    PROVIDER_NAME = "arXiv"

    ATOM_NAMESPACE = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    def __init__(self) -> None:
        self.base_url = settings.ARXIV_API

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Paper]:
        """
        Search arXiv and convert results into Paper objects.
        """

        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:

                response = await client.get(
                    self.base_url,
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
            root = ElementTree.fromstring(response.text)

        except ElementTree.ParseError as exc:
            raise ProviderError(
                message=(
                    f"{self.PROVIDER_NAME} returned "
                    "invalid XML."
                ),
                provider=self.PROVIDER_NAME,
                status_code=response.status_code,
            ) from exc

        papers: List[Paper] = []

        for entry in root.findall(
            "atom:entry",
            self.ATOM_NAMESPACE,
        ):
            paper_id = self._extract_paper_id(entry)
            title = self._extract_text(entry, "title")
            abstract = self._extract_text(entry, "summary")
            published = self._extract_text(entry, "published")

            authors = [
                Author(name=author_name)
                for author_name in self._extract_authors(entry)
            ]

            pdf_url = self._extract_pdf_url(entry)

            year = None

            if published:
                try:
                    year = int(published[:4])
                except ValueError:
                    year = None

            papers.append(
                Paper(
                    paper_id=paper_id,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    citation_count=None,
                    pdf_url=pdf_url,
                    source=self.PROVIDER_NAME,
                )
            )

        return papers

    def _extract_text(
        self,
        entry: ElementTree.Element,
        tag: str,
    ) -> str:
        """
        Extract text from an Atom element.
        """

        element = entry.find(
            f"atom:{tag}",
            self.ATOM_NAMESPACE,
        )

        if element is None or element.text is None:
            return ""

        return element.text.strip()

    def _extract_authors(
        self,
        entry: ElementTree.Element,
    ) -> List[str]:
        """
        Extract author names from an arXiv entry.
        """

        authors = []

        for author in entry.findall(
            "atom:author",
            self.ATOM_NAMESPACE,
        ):
            name = author.find(
                "atom:name",
                self.ATOM_NAMESPACE,
            )

            if name is not None and name.text:
                authors.append(name.text.strip())

        return authors

    def _extract_paper_id(
        self,
        entry: ElementTree.Element,
    ) -> str:
        """
        Extract the arXiv identifier from the entry ID.
        """

        entry_id = self._extract_text(
            entry,
            "id",
        )

        return entry_id.rstrip("/").split("/")[-1]

    def _extract_pdf_url(
        self,
        entry: ElementTree.Element,
    ) -> str | None:
        """
        Extract the PDF download URL from arXiv links.
        """

        for link in entry.findall(
            "atom:link",
            self.ATOM_NAMESPACE,
        ):
            link_type = link.attrib.get("type")
            href = link.attrib.get("href")

            if (
                link_type == "application/pdf"
                and href
            ):
                return href

        return None