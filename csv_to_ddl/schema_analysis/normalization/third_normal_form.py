import logging
from typing import List, Dict

from csv_to_ddl.config.default_config import NormalizationConfig
from csv_to_ddl.schema_analysis.models.table import NormalizationSuggestion, TableSpec
from csv_to_ddl.schema_analysis.normalization.base_normal_form import NormalForm


class ThirdNormalForm(NormalForm):

    def __init__(self, config: NormalizationConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)

    def check(self, table_name: str, header: List[str],
              rows: List[List[str]], table_spec: TableSpec) -> List[NormalizationSuggestion]:
        """
        Third Normal Form violation detection algorithm.
        
        Algorithm detects transitive dependencies where non-key attributes depend
        on other non-key attributes rather than directly on the primary key.
        
        Process:
        1. Identify primary key columns and non-key columns
        2. For each non-key column as potential determinant:
           - Test functional dependencies with other non-key columns
           - Calculate confidence based on consistency and uniqueness
        3. Generate normalization suggestions for splitting tables
        
        Transitive dependency: A → B → C where A is PK, B is non-key, C depends on B
        Solution: Split into two tables to eliminate the transitive path
        
        Returns:
            List of normalization suggestions with proposed table splits
        """
        suggestions = []

        if not table_spec or not rows or not header:
            self.logger.warning(f"Insufficient data to analyze 3NF for columns_and_types {table_name}")
            return suggestions

        if not table_spec.primary_key:
            self.logger.warning(f"No primary key defined for columns_and_types {table_name}")
            return suggestions

        pk_columns = set(table_spec.primary_key.columns)

        all_columns = set(header)
        non_key_columns = all_columns - pk_columns

        if len(non_key_columns) < self.config.nf3_min_non_key_columns:
            return suggestions

        transitive_deps = self._find_transitive_dependencies(header, rows, pk_columns, non_key_columns)

        for dependency in transitive_deps:
            lookup_table_columns = [dependency['determinant']] + dependency['dependents']

            suggestion = NormalizationSuggestion(
                table_name=table_name,
                suggestion_type="3NF",
                description=f"Transitive dependency detected: {', '.join(dependency['dependents'])} depends on "
                            f"{dependency['determinant']}, creating transitive dependency through primary key. "
                            f"Consider extracting to a separate '{dependency['new_table_name']}' columns_and_types with "
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
        """
        Test functional dependency between two columns using determinant mapping.
        
        A functional dependency X → Y exists if each value of X determines
        exactly one value of Y. Algorithm creates a mapping from determinant
        values to dependent values and checks for consistency.
        
        Returns:
            True if functional dependency exists, False if multiple dependent
            values exist for the same determinant value
        """
        dependency_map = {}
        det_values_seen = set()

        for row in rows:
            if len(row) <= max(det_idx, dep_idx):
                continue

            det_value = row[det_idx].strip()
            dep_value = row[dep_idx].strip()

            det_values_seen.add(det_value)

            if det_value in dependency_map:
                # Violation: same determinant maps to different dependent values
                if dependency_map[det_value] != dep_value:
                    return False
            else:
                dependency_map[det_value] = dep_value

        # Functional dependency exists if we have multiple determinant values
        # and each maps to exactly one dependent value
        return 1 < len(det_values_seen) == len(dependency_map)

    def _calculate_dependency_confidence(self, rows: List[List[str]], col_indices: Dict[str, int],
                                         determinant: str, dependents: List[str], pk_columns: set) -> float:
        det_idx = col_indices[determinant]
        det_values, total_rows = self._gather_determinant_values(rows, det_idx)
        
        if total_rows == 0:
            return 0.0
            
        if len(det_values) < self.config.nf3_min_determinant_values:
            return 0.0
            
        if determinant in pk_columns:
            return 0.0

        consistency_score = self._calculate_consistency_score(rows, col_indices, det_idx, dependents)
        base_confidence = self._get_base_confidence(consistency_score)
        uniqueness_bonus = self._calculate_uniqueness_bonus(det_values, total_rows)
        
        return min(1.0, base_confidence + uniqueness_bonus)

    @staticmethod
    def _gather_determinant_values(rows, det_idx):
        det_values = set()
        total_rows = 0

        for row in rows:
            if len(row) > det_idx:
                det_values.add(row[det_idx].strip())
                total_rows += 1
                
        return det_values, total_rows

    def _calculate_consistency_score(self, rows, col_indices, det_idx, dependents):
        consistency_score = 1.0
        
        for dep_col in dependents:
            dep_idx = col_indices[dep_col]
            if not self._check_functional_dependency(rows, det_idx, dep_idx):
                consistency_score -= self.config.nf3_consistency_penalty
                
        return consistency_score

    def _get_base_confidence(self, consistency_score):
        return (self.config.nf3_base_confidence_high_threshold
                if consistency_score > self.config.nf3_consistency_threshold 
                else self.config.nf3_base_confidence_low_threshold)

    def _calculate_uniqueness_bonus(self, det_values, total_rows):
        uniqueness_ratio = len(det_values) / total_rows
        return min(self.config.nf3_max_uniqueness_bonus,
                  uniqueness_ratio * self.config.nf3_uniqueness_bonus_multiplier)
