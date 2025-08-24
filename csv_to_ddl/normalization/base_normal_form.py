from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec


class NormalForm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def check(self, table_name: str,
              table_spec: Optional[TableSpec] = None,
              tables_data: Optional[Dict[str, List[List[str]]]] = None,
              tables_headers: Optional[Dict[str, List[str]]] = None) -> List[NormalizationSuggestion]:
        pass
