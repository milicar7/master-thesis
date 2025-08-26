import logging
from typing import Optional

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.schema_analysis.models.table import TableSpec, PrimaryKeySpec
from csv_to_ddl.schema_analysis.primary_key.pk_scoring import calculate_column_pk_score

logger = logging.getLogger(__name__)


def detect_single_key(table_spec: TableSpec, config: KeyConfig) -> Optional[PrimaryKeySpec]:
    candidates = []

    for col in table_spec.columns:
        if not col.statistics or col.statistics.unique_ratio < config.pk_single_uniqueness_threshold:
            continue

        score = calculate_column_pk_score(col, config)
        score += config.pk_uniqueness_bonus

        if score >= config.pk_single_confidence_threshold:
            candidates.append((col.name, score))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[1], reverse=True)
    col_name, score = candidates[0]

    logger.info(f"Primary key candidate for {table_spec.name}: {col_name} (score: {score:.1f}")

    return PrimaryKeySpec(columns=[col_name],
                          key_type="natural")
