from abc import ABC, abstractmethod
from typing import List, Optional
from models.models import Translation


class BaseWordParser(ABC):
    @abstractmethod
    def parse_article(self, wordcsv: List[str]) -> Optional[List[Translation]]:
        pass
