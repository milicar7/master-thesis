from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.schema_analysis.models.dialects import DataType
from csv_to_ddl.schema_analysis.models.table import ColumnSpec


def calculate_column_pk_score(col: ColumnSpec, config: KeyConfig) -> float:
    score = 0.0

    col_name_lower = col.name.lower()

    if col_name_lower in ['id', 'pk', 'key']:
        score += config.pk_primary_name_bonus
    elif col_name_lower.endswith('_id') or col_name_lower.endswith('id'):
        score += config.pk_id_name_bonus

    if col.data_type in [DataType.INTEGER, DataType.BIGINT, DataType.UUID]:
        score += config.pk_type_bonus

    if col.data_type == DataType.TEXT and col.statistics and col.statistics.avg_length:
        if col.statistics.avg_length > config.pk_text_length_threshold:
            score -= config.pk_long_text_penalty

    return score
