import logging
from typing import Dict, List, Optional

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.models.table import TableSpec, ForeignKeySpec
from csv_to_ddl.schema_analysis.foreign_key_detection.fk_map import get_composite_values_from_data

logger = logging.getLogger(__name__)


def detect_composite_foreign_keys(table_name: str, table_spec: TableSpec,
                                  reference_keys: Dict[str, Dict],
                                  tables_data: Dict[str, List[List[str]]],
                                  config: KeyConfig) -> List[ForeignKeySpec]:
    foreign_keys = []
    table_headers = reference_keys.get(table_name, {}).get('headers', [])

    composite_pk_patterns = _get_composite_pk_patterns(reference_keys, table_name)

    for ref_table, ref_columns in composite_pk_patterns:
        matching_columns = _find_matching_columns(table_spec, ref_columns)

        if matching_columns:
            best_match = _evaluate_composite_match(table_name, matching_columns,
                                                   ref_table, ref_columns,
                                                   reference_keys, tables_data,
                                                   table_headers, config)

            if best_match:
                foreign_keys.append(best_match)
                logger.info(
                    f"Composite foreign key detected: {table_name}.({', '.join(matching_columns)}) -> "
                    f"{ref_table}.({', '.join(ref_columns)}) "
                    f"(confidence: {best_match.confidence:.1%})"
                )

    return foreign_keys


def _get_composite_pk_patterns(reference_keys: Dict[str, Dict], current_table: str) -> List[tuple]:
    patterns = []

    for ref_table, ref_data in reference_keys.items():
        if ref_table == current_table:
            continue

        for composite_key in ref_data.get('composite_keys', {}):
            patterns.append((ref_table, list(composite_key)))

    return patterns


def _find_matching_columns(table_spec: TableSpec, target_columns: List[str]) -> List[str]:
    table_column_names = [col.name for col in table_spec.columns]
    matching = []

    for target_col in target_columns:
        if target_col in table_column_names:
            matching.append(target_col)

    return matching if len(matching) == len(target_columns) else []


def _evaluate_composite_match(table_name: str, source_columns: List[str],
                              ref_table: str, ref_columns: List[str],
                              reference_keys: Dict[str, Dict],
                              tables_data: Dict[str, List[List[str]]],
                              table_headers: List[str],
                              config: KeyConfig) -> Optional[ForeignKeySpec]:
    source_values = get_composite_values_from_data(table_name, source_columns, tables_data, table_headers)
    ref_values = reference_keys[ref_table]['composite_keys'].get(tuple(ref_columns))

    if not source_values or not ref_values:
        return None

    overlap = len(source_values.intersection(ref_values))
    overlap_ratio = overlap / len(source_values)

    if overlap_ratio >= config.fk_overlap_threshold:
        return ForeignKeySpec(
            columns=source_columns,
            referenced_table=ref_table,
            referenced_columns=ref_columns,
            confidence=overlap_ratio,
            match_ratio=overlap_ratio,
            reasoning=f"Exact column name pattern match with {overlap_ratio:.1%} value overlap"
        )

    return None
