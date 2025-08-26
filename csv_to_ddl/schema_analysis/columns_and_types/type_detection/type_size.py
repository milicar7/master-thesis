from csv_to_ddl.config.default_config import TypeConfig
from schema_analysis.models.dialects import DataType, DatabaseDialect, DIALECT_CONFIGS
from schema_analysis.models.table import ColumnSizeSpec


def calculate_size_spec(data_type: DataType, max_detected_length: int, config: TypeConfig) -> ColumnSizeSpec:
    if data_type in [DataType.VARCHAR, DataType.CHAR, DataType.EMAIL]:
        return ColumnSizeSpec(max_length=config.max_varchar_length)
    elif data_type == DataType.CHAR:
        max_length = min(max_detected_length, config.max_varchar_length)
        return ColumnSizeSpec(max_length=max_length)
    elif data_type == DataType.DECIMAL:
        precision = config.decimal_precision_limit
        scale = config.decimal_scale_limit
        return ColumnSizeSpec(precision=precision, scale=scale)
    elif data_type == DataType.UUID:
        return ColumnSizeSpec(max_length=config.uuid_char_length)
    elif data_type == DataType.BOOLEAN:
        return ColumnSizeSpec(max_length=config.boolean_length)
    else:
        return ColumnSizeSpec()


def format_type_with_size(data_type: DataType, size_spec: ColumnSizeSpec, dialect: DatabaseDialect) -> str:
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
        return f"{base_type}({1})"

    return base_type
