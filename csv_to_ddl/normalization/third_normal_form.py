import logging
from typing import List, Optional, Dict

from csv_to_ddl.config.default_config import NormalizationConfig
from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.normalization.base_normal_form import NormalForm


class ThirdNormalForm(NormalForm):

    def __init__(self, config: NormalizationConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)

    def check(self, table_name: str,
              table_spec: TableSpec,
              rows: List[List[str]],
              headers: List[str]) -> List[NormalizationSuggestion]:
        """
        Check for Third Normal Form violations by detecting transitive dependencies.
        
        A table violates 3NF if there are non-key attributes that depend on other 
        non-key attributes (transitive dependency).
        """
        suggestions = []

        if not table_spec or not rows or not headers:
            self.logger.warning(f"Insufficient data to analyze 3NF for table {table_name}")
            return suggestions

        if not table_spec.primary_key:
            self.logger.warning(f"No primary key defined for table {table_name}")
            return suggestions

        pk_columns = set(table_spec.primary_key.columns)

        all_columns = set(headers)
        non_key_columns = all_columns - pk_columns

        if len(non_key_columns) < self.config.nf3_min_non_key_columns:
            return suggestions

        transitive_deps = self._find_transitive_dependencies(headers, rows, pk_columns, non_key_columns)

        for dependency in transitive_deps:
            lookup_table_columns = [dependency['determinant']] + dependency['dependents']

            suggestion = NormalizationSuggestion(
                table_name=table_name,
                suggestion_type="3NF",
                description=f"Transitive dependency detected: {', '.join(dependency['dependents'])} depends on "
                            f"{dependency['determinant']}, creating transitive dependency through primary key. "
                            f"Consider extracting to a separate '{dependency['new_table_name']}' table with "
                            f"columns: {', '.join(lookup_table_columns)}.",
                confidence=dependency['confidence']
            )
            suggestions.append(suggestion)

        return suggestions

    def _find_transitive_dependencies(self, headers: List[str], rows: List[List[str]],
                                      pk_columns: set, non_key_columns: set) -> List[Dict]:
        dependencies = []

        col_indices = {col: idx for idx, col in enumerate(headers)}

        for determinant_col in non_key_columns:
            det_idx = col_indices[determinant_col]

            dependent_cols = []
            for dependent_col in non_key_columns:
                if dependent_col == determinant_col:
                    continue

                dep_idx = col_indices[dependent_col]

                is_dependent = self._check_functional_dependency(rows, det_idx, dep_idx)
                self.logger.debug(f"Checking {determinant_col} -> {dependent_col}: {is_dependent}")
                if is_dependent:
                    dependent_cols.append(dependent_col)

            if dependent_cols:
                confidence = self._calculate_dependency_confidence(rows, col_indices, determinant_col, dependent_cols, pk_columns)
                if confidence > self.config.nf3_confidence_threshold:
                    dependencies.append({
                        'determinant': determinant_col,
                        'dependents': dependent_cols,
                        'description': f"{', '.join(dependent_cols)} depends on {determinant_col}, creating transitive dependency through primary key",
                        'new_table_name': f"{determinant_col.lower()}_details",
                        'confidence': confidence
                    })

        return dependencies

    @staticmethod
    def _check_functional_dependency(rows: List[List[str]], det_idx: int, dep_idx: int) -> bool:
        """Check if column at dep_idx functionally depends on column at det_idx"""
        dependency_map = {}
        det_values_seen = set()

        for row in rows:
            if len(row) <= max(det_idx, dep_idx):
                continue

            det_value = row[det_idx].strip()
            dep_value = row[dep_idx].strip()

            det_values_seen.add(det_value)

            if det_value in dependency_map:
                if dependency_map[det_value] != dep_value:
                    return False
            else:
                dependency_map[det_value] = dep_value

        return 1 < len(det_values_seen) == len(dependency_map)

    def _calculate_dependency_confidence(self, rows: List[List[str]], col_indices: Dict[str, int],
                                         determinant: str, dependents: List[str], pk_columns: set) -> float:
        det_idx = col_indices[determinant]

        det_values = set()
        total_rows = 0

        for row in rows:
            if len(row) > det_idx:
                det_values.add(row[det_idx].strip())
                total_rows += 1

        if total_rows == 0:
            return 0.0

        if len(det_values) < self.config.nf3_min_determinant_values:
            return 0.0

        consistency_score = 1.0
        for dep_col in dependents:
            dep_idx = col_indices[dep_col]
            if not self._check_functional_dependency(rows, det_idx, dep_idx):
                consistency_score -= self.config.nf3_consistency_penalty

        if determinant in pk_columns:
            return 0.0

        base_confidence = self.config.nf3_base_confidence_high_threshold if consistency_score > self.config.nf3_consistency_threshold else self.config.nf3_base_confidence_low_threshold

        uniqueness_ratio = len(det_values) / total_rows
        uniqueness_bonus = min(self.config.nf3_max_uniqueness_bonus,
                               uniqueness_ratio * self.config.nf3_uniqueness_bonus_multiplier)

        return min(1.0, base_confidence + uniqueness_bonus)
