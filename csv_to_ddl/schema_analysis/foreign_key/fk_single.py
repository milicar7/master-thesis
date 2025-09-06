import logging
import re
from typing import Dict, List, Set

from csv_to_ddl.config.default_config import KeyConfig
from schema_analysis.foreign_key.fk_map import get_single_column_values_from_data
from schema_analysis.models.table import ForeignKeySpec, TableSpec

logger = logging.getLogger(__name__)


def detect_single_column_foreign_keys(table_name: str,
                                      table_header: List[str], table_data: List[List[str]], table_spec: TableSpec,
                                      reference_keys: Dict[str, Dict], config: KeyConfig) -> List[ForeignKeySpec]:
    """
    Algorithm for detecting single-column foreign key relationships.
    
    Process:
    1. For each column in the current table:
       - Extract unique values from actual data
       - Compare against all potential reference columns in other tables
    2. For each potential reference relationship:
       - Calculate value overlap ratio (how many values exist in reference table)
       - Apply naming pattern bonuses (matching column names, common FK patterns)
       - Apply primary key bonus if referencing a primary key column
    3. Select best match above confidence threshold for each column
    
    Uses set intersection to efficiently compute overlaps and applies
    heuristic scoring to rank potential relationships.
    
    Args:
        table_name: Name of table being analyzed
        table_header: Column headers for data access
        table_data: Actual data rows
        table_spec: Table specification with column metadata
        reference_keys: Map of all potential reference tables and their key columns
        config: Configuration with FK detection parameters
        
    Returns:
        List of detected foreign key specifications
    """
    foreign_keys = []

    # Analyze each column as potential foreign key
    for col in table_spec.columns:
        col_values = get_single_column_values_from_data(col.name, table_data, table_header)
        if not col_values:
            continue

        best_match = None
        best_score = 0.0

        # Test against all potential reference tables/columns
        for ref_table, ref_data in reference_keys.items():
            if ref_table == table_name:  # Skip self-references
                continue

            for ref_col, ref_values in ref_data['single_keys'].items():
                # Calculate relationship strength score
                match_score, overlap_ratio = _calculate_match_score(col_values, ref_values,
                                                                    col.name, ref_col,
                                                                    ref_table, reference_keys, config)

                if match_score and match_score > best_score:
                    best_score = match_score
                    best_match = ForeignKeySpec(columns=[col.name],
                                                referenced_table=ref_table,
                                                referenced_columns=[ref_col],
                                                confidence=match_score)

        if best_match:
            foreign_keys.append(best_match)
            logger.info(f"Single foreign key detected: {table_name}.{col.name} -> "
                        f"{best_match.referenced_table}.{best_match.referenced_columns[0]} "
                        f"(confidence: {best_match.confidence:.1%})")

    return foreign_keys


def _calculate_match_score(col_values: Set[str], ref_values: Set[str],
                           col_name: str, ref_col_name: str,
                           ref_table: str, reference_keys: Dict[str, Dict],
                           config: KeyConfig) -> tuple[float, float]:
    is_valid, overlap_ratio = _is_valid_fk_relationship(col_values, ref_values, config)
    if not is_valid:
        return 0.0, overlap_ratio

    ref_table_data = reference_keys.get(ref_table, {})
    pk_columns = ref_table_data.get('primary_key_columns', set())
    pk_bonus = _get_primary_key_bonus(ref_col_name, pk_columns, config)

    naming_score = _get_naming_score(col_name, ref_col_name, ref_table, config)
    is_generic_column = (_is_generic_column_name(col_name) and _is_generic_column_name(ref_col_name))

    if is_generic_column:
        base_score = overlap_ratio * config.fk_validity_bonus
        final_score = base_score + pk_bonus

        if overlap_ratio >= config.fk_overlap_threshold and final_score >= config.fk_validation_threshold:
            return final_score, overlap_ratio
        else:
            return 0.0, overlap_ratio

    if naming_score == 0.0:
        return 0.0, overlap_ratio

    base_score = (overlap_ratio * config.fk_validity_bonus + naming_score * config.fk_naming_bonus)
    final_score = base_score + pk_bonus

    return max(0.0, final_score), overlap_ratio


def _is_valid_fk_relationship(col_values: Set[str], ref_values: Set[str], config: KeyConfig) -> tuple[bool, float]:
    validation_score = 0.0

    total = len(col_values)
    if total == 0:
        return False, 0.0

    overlap = len(col_values.intersection(ref_values))
    overlap_ratio = overlap / total
    if overlap_ratio > config.fk_overlap_threshold:
        overlap_score = overlap_ratio * config.fk_validation_overlap_bonus
        validation_score += overlap_score

        col_size = len(col_values)
        size_ratio = len(ref_values) / max(1, col_size)
        size_score = min(1.0, size_ratio) * config.fk_validation_size_bonus
        validation_score += size_score

        return validation_score >= config.fk_validation_threshold, overlap_ratio
    else:
        return False, overlap_ratio


def _get_naming_score(col_name: str, ref_col_name: str, ref_table: str, config: KeyConfig) -> float:
    col_lower = col_name.lower()
    ref_col_lower = ref_col_name.lower()
    ref_table_lower = ref_table.lower()

    if col_lower == ref_col_lower:
        return config.fk_exact_match_bonus

    if col_lower.endswith('_id') and ref_col_lower == 'id':
        expected_prefix = col_lower[:-3]
        if expected_prefix == ref_table_lower or expected_prefix in ref_table_lower:
            return config.fk_table_prefix_bonus

    if ref_table_lower in col_lower:
        return config.fk_table_reference_bonus

    col_words = [word for word in col_lower.split('_') if len(word) > 2]
    if any(word in ref_table_lower for word in col_words):
        return config.fk_word_match_bonus

    return 0.0


def _get_primary_key_bonus(ref_col_name: str, pk_columns: set, config: KeyConfig) -> float:
    if ref_col_name in pk_columns:
        return config.fk_primary_key_target_bonus

    return 0.0


def _is_generic_column_name(col_name: str) -> bool:
    return bool(re.match(r'^column_\d+$', col_name.lower()))
