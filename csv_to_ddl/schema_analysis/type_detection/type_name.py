import statistics
from typing import Dict, Any
from typing import List, Tuple

from csv_to_ddl.config.default_config import TypeConfig
from csv_to_ddl.models.dialects import DataType
from csv_to_ddl.schema_analysis.type_detection.utils import (is_boolean, is_integer, is_bigint, is_float, is_decimal,
                                                             is_uuid,
                                                             is_email, is_url, is_datetime, is_date, is_time, is_json)


def detect_column_type(values: List[str], config: TypeConfig) -> Tuple[DataType, Dict[str, Any]]:
    if not values:
        return DataType.TEXT, {'reason': 'no_values'}

    non_empty_values = [str(v).strip() for v in values if v is not None and str(v).strip()]

    if not non_empty_values:
        return DataType.TEXT, {'reason': 'all_empty'}

    sample_values = non_empty_values[:min(len(non_empty_values), config.type_detection_sample_size)]

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

    for test_func, data_type in type_tests:
        match_ratio, metadata = test_func(sample_values)
        if match_ratio >= config.type_detection_confidence_threshold:
            return data_type, {'match_ratio': match_ratio, **metadata}

    lengths = [len(v) for v in sample_values]
    max_length = max(lengths) if lengths else 0
    avg_length = statistics.mean(lengths) if lengths else 0

    if max_length <= 1 and all(len(v) == 1 for v in sample_values):
        return DataType.CHAR, {'max_length': max_length, 'avg_length': avg_length}
    elif max_length <= config.max_varchar_length:
        return DataType.VARCHAR, {'max_length': max_length, 'avg_length': avg_length}
    else:
        return DataType.TEXT, {'max_length': max_length, 'avg_length': avg_length}
