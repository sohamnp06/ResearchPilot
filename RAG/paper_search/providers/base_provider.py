from abc import ABC, abstractmethod
from typing import List

from paper_search.models import Paper


class BaseProvider(ABC):

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Paper]:
        """
        Search papers.

        Returns
        -------
        List[Paper]
        """
        pass