from typing import Dict, Any

from csv_to_ddl.config.default_config import TypeConfig
from csv_to_ddl.models.dialects import DataType, DatabaseDialect, DIALECT_CONFIGS
from csv_to_ddl.models.table import ColumnSizeSpec


def calculate_size_spec(data_type: DataType, metadata: Dict[str, Any], config: TypeConfig) -> ColumnSizeSpec:
    if data_type in [DataType.VARCHAR, DataType.CHAR, DataType.EMAIL]:
        detected_max = metadata.get('max_length', 0)
        buffer_multiplier = config.char_buffer_multiplier if data_type == DataType.CHAR else config.varchar_buffer_multiplier
        buffered_length = detected_max * buffer_multiplier
        max_length = min(buffered_length, config.max_varchar_length)
        return ColumnSizeSpec(max_length=max_length)
    elif data_type == DataType.DECIMAL:
        avg_decimal_places = metadata.get('avg_decimal_places', 2)
        scale = min(int(round(avg_decimal_places)), config.decimal_scale_limit)
        precision = min(config.decimal_precision_max,
                        max(config.decimal_precision_min, scale + config.decimal_integer_buffer))
        return ColumnSizeSpec(precision=precision, scale=scale)
    elif data_type == DataType.UUID:
        return ColumnSizeSpec(max_length=config.uuid_char_length)
    else:
        return ColumnSizeSpec()


def format_type_with_size(data_type: DataType, size_spec: ColumnSizeSpec, dialect: DatabaseDialect,
                          type_config: TypeConfig) -> str:
    config = DIALECT_CONFIGS[dialect]
    base_type = config.type_mappings.get(data_type, data_type.value)

    if data_type in [DataType.VARCHAR, DataType.CHAR, DataType.EMAIL] and size_spec.max_length:
        return f"{base_type}({size_spec.max_length})"
    elif data_type == DataType.DECIMAL:
        if size_spec.precision and size_spec.scale is not None:
            return f"{base_type}({size_spec.precision},{size_spec.scale})"
        elif size_spec.precision:
            return f"{base_type}({size_spec.precision})"
    elif data_type == DataType.UUID and not config.supports_uuid and size_spec.max_length:
        return f"{base_type}({size_spec.max_length})"
    elif data_type == DataType.BOOLEAN and config.boolean_needs_size:
        return f"{base_type}({type_config.boolean_size})"

    return base_type
