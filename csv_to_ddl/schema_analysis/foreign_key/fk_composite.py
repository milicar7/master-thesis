import logging
from typing import Dict, List, Optional

from csv_to_ddl.config.default_config import KeyConfig
from schema_analysis.foreign_key.fk_map import get_composite_values_from_data
from schema_analysis.models.table import TableSpec, ForeignKeySpec

logger = logging.getLogger(__name__)


def detect_composite_foreign_keys(table_name: str,
                                  table_header: List[str], table_data: List[List[str]], table_spec: TableSpec,
                                  reference_keys: Dict[str, Dict], config: KeyConfig) -> List[ForeignKeySpec]:
    """
    Algorithm for detecting multi-column composite foreign key relationships.
    
    Process:
    1. Extract composite primary key patterns from all reference tables
    2. For each composite PK pattern:
       - Find matching column names in current table
       - Test value overlap using tuple-based comparison
       - Calculate confidence based on overlap ratio and naming similarity
    3. Select best matches above confidence threshold
    
    Handles relationships like:
    - order_items(product_id, supplier_id) → products(product_id, supplier_id)
    - Uses tuple-based set intersection for multi-column value matching
    
    More complex than single FK detection due to combinatorial column matching
    and multidimensional value space analysis.
    
    Returns:
        List of composite foreign key specifications with confidence scores
    """
    foreign_keys = []

    composite_pk_patterns = _get_composite_pk_patterns(reference_keys, table_name)

    for ref_table, ref_columns in composite_pk_patterns:
        matching_columns = _find_matching_columns(table_spec, ref_columns)

        if matching_columns:
            ref_composite_keys = reference_keys[ref_table]['composite_keys']
            best_match = _evaluate_composite_match(matching_columns,
                                                   ref_table, ref_columns,
                                                   ref_composite_keys, table_data,
                                                   table_header, config)

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


def _evaluate_composite_match(source_columns: List[str],
                              ref_table: str, ref_columns: List[str],
                              ref_composite_keys: Dict,
                              table_data: List[List[str]],
                              table_header: List[str],
                              config: KeyConfig) -> Optional[ForeignKeySpec]:
    source_values = get_composite_values_from_data(source_columns, table_header, table_data)
    ref_values = ref_composite_keys.get(tuple(ref_columns))

    if not source_values or not ref_values:
        return None

    overlap = len(source_values.intersection(ref_values))
    overlap_ratio = overlap / len(source_values)

    if overlap_ratio >= config.fk_overlap_threshold:
        return ForeignKeySpec(
            columns=source_columns,
            referenced_table=ref_table,
            referenced_columns=ref_columns,
            confidence=overlap_ratio)

    return None
