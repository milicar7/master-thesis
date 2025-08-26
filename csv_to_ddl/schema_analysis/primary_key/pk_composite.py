import itertools
from typing import List, Optional, Tuple

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.schema_analysis.models.table import TableSpec, PrimaryKeySpec, ColumnSpec
from csv_to_ddl.schema_analysis.primary_key.pk_scoring import calculate_column_pk_score


def detect_composite_primary_key(table_spec: TableSpec, rows: List[List[str]],
                                 headers: List[str], config: KeyConfig) -> Optional[PrimaryKeySpec]:
    if len(table_spec.columns) < config.pk_composite_size:
        return None

    best_composite = None
    best_score = 0.0

    for col_combination in itertools.combinations(table_spec.columns, config.pk_composite_size):
        col_names = [col.name for col in col_combination]

        uniqueness = _test_composite_uniqueness(col_names, rows, headers)

        if uniqueness >= config.pk_composite_uniqueness_threshold:
            score = _calculate_composite_score(col_combination, config)

            if score > best_score:
                best_score = score
                best_composite = PrimaryKeySpec(columns=col_names,
                                                key_type="composite")

    return best_composite


def _test_composite_uniqueness(col_names: List[str], rows: List[List[str]], headers: List[str]) -> float:
    try:
        col_indices = [headers.index(col_name) for col_name in col_names]
    except ValueError:
        return 0.0

    combinations = []
    for row in rows:
        if len(row) > max(col_indices):
            combo = tuple(row[i] for i in col_indices)
            if all(val is not None and str(val).strip() != '' for val in combo):
                combinations.append(combo)

    if not combinations:
        return 0.0

    unique_combinations = len(set(combinations))
    total_combinations = len(combinations)

    return unique_combinations / total_combinations


def _calculate_composite_score(columns: Tuple[ColumnSpec, ...], config: KeyConfig) -> float:
    score = 0.0

    for col in columns:
        if not col.statistics:
            continue
        col_score = calculate_column_pk_score(col, config)
        score += col_score

    return score
