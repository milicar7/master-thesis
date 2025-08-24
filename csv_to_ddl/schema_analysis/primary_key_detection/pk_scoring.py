from typing import List, Tuple

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.models.dialects import DataType
from csv_to_ddl.models.table import ColumnSpec


def calculate_column_pk_score(col: ColumnSpec, config: KeyConfig) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []

    if not col.nullable:
        score += config.pk_not_nullable_bonus
        reasons.append("not nullable")

    name_score, name_reasons = _calculate_name_score(col.name, config)
    score += name_score
    reasons.extend(name_reasons)

    if col.data_type in [DataType.INTEGER, DataType.BIGINT, DataType.UUID]:
        score += config.pk_uuid_type_bonus
        reasons.append(f"good PK data type ({col.data_type.value})")

    if col.data_type == DataType.TEXT and col.statistics and col.statistics.avg_length:
        if col.statistics.avg_length > config.pk_text_length_threshold:
            score -= config.pk_long_text_penalty
            reasons.append("long text field")
    
    return score, reasons


def _calculate_name_score(col_name: str, config: KeyConfig) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []
    
    col_name_lower = col_name.lower()
    
    if col_name_lower in ['id', 'pk', 'key']:
        score += config.pk_primary_name_bonus
        reasons.append("name indicates primary key")
    elif col_name_lower.endswith('_id') or col_name_lower.endswith('id'):
        score += config.pk_id_name_bonus
        reasons.append("name suggests identifier")
    elif col_name_lower.startswith('id_') or 'uuid' in col_name_lower:
        score += config.pk_uuid_type_bonus
        reasons.append("name suggests identifier")
    
    return score, reasons