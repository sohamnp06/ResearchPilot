from abc import ABC, abstractmethod
from typing import List
from RAG.paper_search.models import Paper


class BaseProvider(ABC):
    """
    Base interface for all paper search providers.
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Paper]:
        """
        Search papers and return Paper objects.
        """
        raise NotImplementedError