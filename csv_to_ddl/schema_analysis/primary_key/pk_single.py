import logging
from typing import Optional

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.schema_analysis.models.table import TableSpec, PrimaryKeySpec
from csv_to_ddl.schema_analysis.primary_key.pk_scoring import calculate_column_pk_score

logger = logging.getLogger(__name__)


def detect_single_key(table_spec: TableSpec, config: KeyConfig) -> Optional[PrimaryKeySpec]:
    """
    Algorithm for detecting single-column natural primary keys.
    
    Process:
    1. Filter columns by uniqueness threshold (must be highly unique)
    2. Calculate composite score based on:
       - Column name patterns (id, key, etc.)
       - Data type appropriateness (integers preferred)
       - Statistical properties (uniqueness, null ratio)
    3. Apply uniqueness bonus for qualifying columns
    4. Select highest scoring candidate above confidence threshold
    
    Args:
        table_spec: Table specification with column metadata
        config: Configuration with thresholds and scoring parameters
        
    Returns:
        PrimaryKeySpec if suitable candidate found, None otherwise
    """
    candidates = []

    for col in table_spec.columns:
        if col.nullable:
            continue
            
        if not col.statistics or col.statistics.unique_ratio < config.pk_uniqueness_threshold:
            continue

        score = calculate_column_pk_score(col, config)
        candidates.append((col.name, score))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[1], reverse=True)
    col_name, score = candidates[0]

    logger.info(f"Primary key candidate for {table_spec.name}: {col_name} (score: {score:.1f}")

    return PrimaryKeySpec(columns=[col_name],
                          key_type="natural")
