import logging
from typing import Dict, List

from csv_to_ddl.config.default_config import NormalizationConfig
from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.normalization.base_normal_form import NormalForm


class SecondNormalForm(NormalForm):

    def __init__(self, config: NormalizationConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)

    def check(self, table_name: str,
              rows: List[List[str]],
              headers: List[str],
              table_spec: TableSpec) -> List[NormalizationSuggestion]:
        """Check for Second Normal Form violations (partial dependencies)"""
        suggestions = []

        if not self._should_check_2nf(table_spec):
            return suggestions

        if rows and headers:
            suggestions.extend(self._check_2nf(
                table_name, table_spec, rows, headers
            ))

        return suggestions

    @staticmethod
    def _should_check_2nf(table_spec: TableSpec) -> bool:
        if not table_spec:
            return False
        return table_spec.primary_key and len(table_spec.primary_key.columns) > 1

    def _check_2nf(self, table_name: str, table_spec: TableSpec,
                   rows: List[List[str]],
                   headers: List[str]) -> List[NormalizationSuggestion]:
        suggestions = []
        pk_columns = table_spec.primary_key.columns
        pk_indices = self._get_pk_indices(pk_columns, headers)

        if len(pk_indices) < 2:
            return suggestions

        non_key_columns = [col for col in table_spec.columns if col.name not in pk_columns]
        partial_dependencies = self._find_partial_dependencies(non_key_columns, rows, headers, pk_columns, pk_indices)

        for dependency in partial_dependencies:
            partial_key_clean = dependency['partial_key'].lower().replace('_id', '').replace('id', '')
            dependent_col_clean = dependency['column'].lower().replace('_name', '').replace('name', '')

            if dependent_col_clean and partial_key_clean != dependent_col_clean:
                proposed_table_name = f"{partial_key_clean}_{dependent_col_clean}"
            else:
                proposed_table_name = f"{partial_key_clean}s" if not partial_key_clean.endswith(
                    's') else partial_key_clean

            suggestion = NormalizationSuggestion(
                table_name=table_name,
                suggestion_type="2NF",
                description=f"Column '{dependency['column']}' has partial dependency on "
                            f"'{dependency['partial_key']}' (part of composite key {pk_columns}) "
                            f"instead of depending on the full key (strength: {dependency['strength']:.1%}). "
                            f"Consider extracting to a separate '{proposed_table_name}' table with "
                            f"columns: {dependency['partial_key']}, {dependency['column']}.",
                confidence=dependency['strength']
            )
            suggestions.append(suggestion)

        return suggestions

    @staticmethod
    def _get_pk_indices(pk_columns: List[str], headers: List[str]) -> List[int]:
        pk_indices = []
        for pk_col in pk_columns:
            try:
                pk_indices.append(headers.index(pk_col))
            except ValueError:
                continue
        return pk_indices

    def _find_partial_dependencies(self, non_key_columns: List, rows: List[List[str]],
                                   headers: List[str], pk_columns: List[str],
                                   pk_indices: List[int]) -> List[Dict]:
        dependencies = []

        if len(rows) < self.config.nf2_min_rows_for_analysis:
            return dependencies

        for col in non_key_columns:
            try:
                col_index = headers.index(col.name)
            except ValueError:
                continue

            col_values = set()
            for row in rows:
                if len(row) > col_index and row[col_index] and str(row[col_index]).strip():
                    col_values.add(row[col_index])

            if len(col_values) < self.config.nf2_min_column_values:
                continue

            for i, pk_part_index in enumerate(pk_indices):
                partial_dependency_strength = self._check_partial_dependency(
                    rows, col_index, [pk_part_index], pk_indices
                )

                if partial_dependency_strength >= self.config.nf2_partial_dependency_threshold:
                    dependencies.append({
                        'column': col.name,
                        'partial_key': pk_columns[i],
                        'strength': partial_dependency_strength
                    })

        return dependencies

    def _check_partial_dependency(self, rows, dependent_col_index,
                                  partial_key_indices, full_key_indices):
        partial_key_groups = {}
        full_key_groups = {}

        for row in rows:
            if len(row) > max(partial_key_indices + full_key_indices + [dependent_col_index]):
                partial_key_vals = [row[i] for i in partial_key_indices]
                full_key_vals = [row[i] for i in full_key_indices]
                dependent_val = row[dependent_col_index]

                if any(val is None or str(val).strip() == '' for val in
                       partial_key_vals + full_key_vals + [dependent_val]):
                    continue

                partial_key = tuple(partial_key_vals)
                full_key = tuple(full_key_vals)

                if partial_key not in partial_key_groups:
                    partial_key_groups[partial_key] = []
                partial_key_groups[partial_key].append(dependent_val)

                if full_key not in full_key_groups:
                    full_key_groups[full_key] = []
                full_key_groups[full_key].append(dependent_val)

        partial_determinations = sum(1 for vals in partial_key_groups.values() if len(set(vals)) == 1)
        partial_total = len(partial_key_groups)

        full_determinations = sum(1 for vals in full_key_groups.values() if len(set(vals)) == 1)
        full_total = len(full_key_groups)

        if partial_total == 0 or full_total == 0:
            return 0.0

        partial_strength = partial_determinations / partial_total
        full_strength = full_determinations / full_total

        if full_strength < self.config.nf2_full_key_strength_threshold:
            return 0.0

        if full_strength > 0:
            dependency_ratio = partial_strength / full_strength
            return dependency_ratio if partial_strength > self.config.nf2_partial_strength_threshold else 0.0

        return partial_strength if partial_strength > self.config.nf2_min_partial_strength else 0.0
