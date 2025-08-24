import logging
from typing import Optional

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.models.table import TableSpec, PrimaryKeySpec
from csv_to_ddl.schema_analysis.primary_key_detection.pk_scoring import calculate_column_pk_score

logger = logging.getLogger(__name__)


def detect_single_key(table_spec: TableSpec, config: KeyConfig) -> Optional[PrimaryKeySpec]:
    candidates = []

    for col in table_spec.columns:
        if not col.statistics or col.statistics.unique_ratio < config.pk_single_uniqueness_threshold:
            continue

        score, reasons = calculate_column_pk_score(col, config)
        score += config.pk_uniqueness_bonus
        reasons.append(f"high uniqueness ({col.statistics.unique_ratio:.1%})")

        if score >= config.pk_single_confidence_threshold:
            candidates.append((col.name, score, reasons))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[1], reverse=True)
    col_name, score, reasons = candidates[0]

    logger.info(
        f"Primary key candidate for {table_spec.name}: {col_name} (score: {score:.1f}, reasons: {', '.join(reasons)})")

    return PrimaryKeySpec(columns=[col_name],
                          key_type="natural",
                          confidence=1.0,
                          reasoning="; ".join(reasons))
