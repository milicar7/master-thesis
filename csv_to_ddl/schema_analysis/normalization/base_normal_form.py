from abc import ABC, abstractmethod
from typing import List

from csv_to_ddl.schema_analysis.models.table import NormalizationSuggestion
from csv_to_ddl.schema_analysis.models.table import TableSpec


class NormalForm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def check(self, table_name: str, header: List[str],
              rows: List[List[str]], table_spec: TableSpec) -> List[NormalizationSuggestion]:
        pass
