from abc import ABC, abstractmethod
from typing import List

from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec


class NormalForm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def check(self, table_name: str,
              rows: List[List[str]],
              headers: List[str],
              table_spec: TableSpec) -> List[NormalizationSuggestion]:
        pass
