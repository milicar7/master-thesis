import logging
from typing import Dict, List, Optional

from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.normalization.base_normal_form import NormalForm


class FirstNormalForm(NormalForm):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def check(self, table_name: str, table_spec: Optional[TableSpec] = None,
              tables_data: Optional[Dict[str, List[List[str]]]] = None,
              tables_headers: Optional[Dict[str, List[str]]] = None) -> List[NormalizationSuggestion]:
        """Check for First Normal Form violations (multivalued attributes)"""
        suggestions = []

        if not tables_data or not tables_headers:
            return suggestions

        rows = tables_data.get(table_name, [])
        headers = tables_headers.get(table_name, [])

        if not rows or not headers:
            return suggestions

        for col_idx, col_name in enumerate(headers):
            multi_value_indicators = [',', ';', '|', '\n', '\t']
            multi_value_count = 0
            total_count = 0

            for row in rows:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = str(row[col_idx]).strip()
                    total_count += 1

                    for indicator in multi_value_indicators:
                        if indicator in cell_value:
                            multi_value_count += 1
                            break

            if total_count > 0:
                multi_value_ratio = multi_value_count / total_count

                if multi_value_ratio >= 0.1:
                    description = (
                        f"Column '{col_name}' contains multi-valued data in {multi_value_ratio:.1%} of rows. "
                        f"Consider splitting into separate columns or creating a separate '{col_name}_values' table.")

                    suggestion = NormalizationSuggestion(
                        table_name=table_name,
                        suggestion_type="1NF",
                        description=description,
                        confidence=multi_value_ratio
                    )
                    suggestions.append(suggestion)

        return suggestions
