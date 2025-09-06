import itertools
from typing import List, Optional

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.schema_analysis.models.table import TableSpec, PrimaryKeySpec
from csv_to_ddl.schema_analysis.primary_key.pk_scoring import calculate_column_pk_score


def detect_composite_primary_key(table_spec: TableSpec, rows: List[List[str]],
                                 headers: List[str], config: KeyConfig) -> Optional[PrimaryKeySpec]:
    """
    Algorithm for detecting multi-column composite primary keys.
    
    Process:
    1. Check if table has enough columns for composite key
    2. Generate all possible column combinations of specified size
    3. For each combination:
       - Test uniqueness by creating tuples from actual data
       - Calculate composite score (sum of individual column scores)
       - Select combination with the highest score above threshold
    
    This addresses cases where no single column is unique enough,
    but a combination of columns provides sufficient uniqueness.
    
    Args:
        table_spec: Table specification with column metadata
        rows: Actual data rows for uniqueness testing
        headers: Column headers for index mapping
        config: Configuration with composite key parameters
        
    Returns:
        PrimaryKeySpec for best composite key, None if no suitable combination found
    """
    if len(table_spec.columns) < config.pk_composite_size:
        return None

    best_composite = None
    best_score = 0.0

    non_nullable_columns = [col for col in table_spec.columns if not col.nullable]

    if len(non_nullable_columns) < config.pk_composite_size:
        return None

    for col_combination in itertools.combinations(non_nullable_columns, config.pk_composite_size):
        score = 0
        col_names = [col.name for col in col_combination]

        uniqueness = _test_composite_uniqueness(col_names, rows, headers)

        if uniqueness >= config.pk_uniqueness_threshold:
            for col in col_combination:
                if not col.statistics:
                    continue
                col_score = calculate_column_pk_score(col, config)
                score += col_score

            if score > best_score:
                best_score = score
                best_composite = PrimaryKeySpec(columns=col_names,
                                                key_type="composite")

    return best_composite


def _test_composite_uniqueness(col_names: List[str], rows: List[List[str]], headers: List[str]) -> float:
    """
    Test uniqueness of column combination using actual data.

    Creates tuples from specified columns across all rows and measures
    the ratio of unique tuples to total tuples. Filters out rows with
    null or empty values to ensure data quality.

    Returns:
        Uniqueness ratio (0.0 to 1.0), where 1.0 means all combinations are unique
    """
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
