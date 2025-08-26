from typing import List

from config.default_config import TypeConfig
from schema_analysis.columns_and_types.type_detection.type_detectors import (is_boolean, is_integer, is_bigint,
                                                                             is_decimal, is_float, is_uuid, is_email,
                                                                             is_url, is_datetime, is_date, is_time,
                                                                             is_json)
from schema_analysis.models.dialects import DataType


def detect_column_type(values: List[str], config: TypeConfig) -> DataType:
    if not values:
        return DataType.TEXT

    non_empty_values = [str(v).strip() for v in values if v is not None and str(v).strip()]

    if not non_empty_values:
        return DataType.TEXT

    type_tests = [
        (is_boolean, DataType.BOOLEAN),
        (is_integer, DataType.INTEGER),
        (is_bigint, DataType.BIGINT),
        (is_decimal, DataType.DECIMAL),
        (is_float, DataType.FLOAT),
        (is_uuid, DataType.UUID),
        (is_email, DataType.EMAIL),
        (is_url, DataType.URL),
        (is_datetime, DataType.DATETIME),
        (is_date, DataType.DATE),
        (is_time, DataType.TIME),
        (is_json, DataType.JSON),
    ]

    sample_values = non_empty_values[:min(len(non_empty_values), config.type_detection_sample_size)]

    for test_func, data_type in type_tests:
        match_ratio = test_func(sample_values)
        if match_ratio >= config.type_detection_confidence_threshold:
            return data_type

    lengths = [len(v) for v in sample_values]
    max_length = max(lengths) if lengths else 0
    if max_length <= 1 and all(len(v) == 1 for v in sample_values):
        return DataType.CHAR
    elif max_length <= config.max_varchar_length:
        return DataType.VARCHAR
    else:
        return DataType.TEXT
