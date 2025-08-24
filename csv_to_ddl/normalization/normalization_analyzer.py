import logging
import re
from typing import Dict, List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.normalization.first_normal_form import FirstNormalForm
from csv_to_ddl.normalization.second_normal_form import SecondNormalForm
from csv_to_ddl.normalization.third_normal_form import ThirdNormalForm


class NormalizationAnalyzer:

    def __init__(self):
        self.config = ConfigManager.get_normalization_config()
        self.first_nf = FirstNormalForm()
        self.second_nf = SecondNormalForm(self.config)
        self.third_nf = ThirdNormalForm(self.config)
        self.logger = logging.getLogger(__name__)

    def analyze(self, table_specs: Dict[str, TableSpec],
                tables_data: Dict[str, List[List[str]]],
                tables_headers: Dict[str, List[str]]) -> List[NormalizationSuggestion]:
        suggestions = []

        for table_name, table_spec in table_specs.items():
            current_suggestions = self._analyze_progressive_normalization(table_name, table_spec,
                                                                          tables_data, tables_headers)
            suggestions.extend(current_suggestions)

        return suggestions

    def _analyze_progressive_normalization(self, table_name: str, table_spec: TableSpec,
                                           tables_data: Dict[str, List[List[str]]],
                                           tables_headers: Dict[str, List[str]]) -> List[NormalizationSuggestion]:
        """Analyze normalization progressively, simulating fixes at each level"""
        all_suggestions = []

        first_nf_violations = self.first_nf.check(table_name,
                                                  tables_data=tables_data,
                                                  tables_headers=tables_headers)
        all_suggestions.extend(first_nf_violations)
        simulated_1nf_data, simulated_1nf_headers, simulated_1nf_spec = self._simulate_1nf_fixes(table_name, table_spec,
                                                                                                 tables_data,
                                                                                                 tables_headers,
                                                                                                 first_nf_violations)

        second_nf_violations = self.second_nf.check(table_name,
                                                    table_spec=simulated_1nf_spec,
                                                    tables_data=simulated_1nf_data,
                                                    tables_headers=simulated_1nf_headers)
        for suggestion in second_nf_violations:
            if first_nf_violations:
                suggestion.description = f"[After 1NF fixes] {suggestion.description}"
        all_suggestions.extend(second_nf_violations)

        simulated_2nf_data, simulated_2nf_headers, simulated_2nf_spec = self._simulate_2nf_fixes(table_name,
                                                                                                 simulated_1nf_spec,
                                                                                                 simulated_1nf_data,
                                                                                                 simulated_1nf_headers,
                                                                                                 second_nf_violations)
        third_nf_violations = self.third_nf.check(table_name,
                                                  table_spec=simulated_2nf_spec,
                                                  tables_data=simulated_2nf_data,
                                                  tables_headers=simulated_2nf_headers)

        for suggestion in third_nf_violations:
            dependencies = []
            if first_nf_violations:
                dependencies.append("1NF")
            if second_nf_violations:
                dependencies.append("2NF")
            if dependencies:
                suggestion.description = f"[After {' & '.join(dependencies)} fixes] {suggestion.description}"

        all_suggestions.extend(third_nf_violations)

        return all_suggestions

    def _simulate_1nf_fixes(self, table_name: str, table_spec: TableSpec,
                            tables_data: Dict[str, List[List[str]]],
                            tables_headers: Dict[str, List[str]],
                            violations: List[NormalizationSuggestion]) -> tuple:
        if not violations or table_name not in tables_data:
            return tables_data, tables_headers, table_spec

        original_headers = tables_headers[table_name]
        original_rows = tables_data[table_name]

        normalized_rows = []

        for row in original_rows:
            expanded_rows = [row]

            for col_idx, cell_value in enumerate(row):
                if isinstance(cell_value, str) and ',' in cell_value and col_idx < len(original_headers):
                    values = [v.strip() for v in cell_value.split(',') if v.strip()]
                    if len(values) > 1:
                        new_expanded_rows = []
                        for existing_row in expanded_rows:
                            for value in values:
                                new_row = existing_row.copy()
                                new_row[col_idx] = value
                                new_expanded_rows.append(new_row)
                        expanded_rows = new_expanded_rows

            normalized_rows.extend(expanded_rows)

        new_tables_data = tables_data.copy()
        new_tables_data[table_name] = normalized_rows

        self.logger.info(
            f"1NF simulation: Expanded {len(original_rows)} rows to {len(normalized_rows)} rows for table '{table_name}'")

        return new_tables_data, tables_headers, table_spec

    def _simulate_2nf_fixes(self, table_name: str, table_spec: TableSpec,
                            tables_data: Dict[str, List[List[str]]],
                            tables_headers: Dict[str, List[str]],
                            violations: List[NormalizationSuggestion]) -> tuple:
        if not violations or table_name not in tables_data:
            return tables_data, tables_headers, table_spec

        headers = tables_headers[table_name]
        rows = tables_data[table_name]

        partially_dependent_columns = set()

        for violation in violations:
            match = re.search(r"Column '([^']+)' has partial dependency", violation.description)
            if match:
                partially_dependent_columns.add(match.group(1))

        if not partially_dependent_columns:
            return tables_data, tables_headers, table_spec

        new_columns = []
        removed_column_indices = []

        for i, col in enumerate(table_spec.columns):
            if col.name in partially_dependent_columns:
                removed_column_indices.append(headers.index(col.name))
            else:
                new_columns.append(col)

        new_headers = [h for i, h in enumerate(headers) if i not in removed_column_indices]

        new_rows = []
        for row in rows:
            new_row = [cell for i, cell in enumerate(row) if i not in removed_column_indices]
            new_rows.append(new_row)

        unique_rows = []
        seen_rows = set()
        for row in new_rows:
            row_tuple = tuple(row)
            if row_tuple not in seen_rows:
                seen_rows.add(row_tuple)
                unique_rows.append(row)

        new_table_spec = TableSpec(
            name=table_spec.name,
            columns=new_columns,
            primary_key=table_spec.primary_key,
            foreign_keys=table_spec.foreign_keys,
            row_count=len(unique_rows),
            source_files=table_spec.source_files
        )

        new_tables_data = tables_data.copy()
        new_tables_data[table_name] = unique_rows

        new_tables_headers = tables_headers.copy()
        new_tables_headers[table_name] = new_headers

        self.logger.info(
            f"2NF simulation: Removed {len(partially_dependent_columns)} partially dependent columns from table '{table_name}'")
        self.logger.info(f"2NF simulation: Reduced {len(rows)} rows to {len(unique_rows)} unique rows")

        return new_tables_data, new_tables_headers, new_table_spec
