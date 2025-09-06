from typing import List

from config.default_config import TypeConfig
from schema_analysis.columns_and_types.type_detection.type_detectors import (is_boolean, is_integer, is_bigint,
                                                                             is_decimal, is_float, is_uuid, is_email,
                                                                             is_url, is_datetime, is_date, is_time,
                                                                             is_json)
from schema_analysis.models.dialects import DataType


def detect_column_type(values: List[str], config: TypeConfig) -> DataType:
    """
    Multi-stage data type detection algorithm using confidence-based scoring.
    
    Process:
    1. Filter out null/empty values for reliable analysis
    2. Test values against ordered list of type detectors:
       - Structured types first (boolean, numeric, UUID, email, URL)
       - Date/time types with various format recognition
       - JSON for complex nested data
    3. Each detector returns confidence ratio (0.0-1.0)
    4. Select first type meeting confidence threshold
    5. Fallback to string types based on length analysis:
       - CHAR for single characters
       - VARCHAR for short strings
       - TEXT for long strings
    
    Ordering is critical: more specific types tested first to avoid
    false positives (e.g., "123" could be integer or varchar).
    
    Args:
        values: All values in the column
        config: Type detection configuration with thresholds
        
    Returns:
        Most appropriate SQL data type based on content analysis
    """
    if not values:
        return DataType.TEXT

    non_empty_values = [str(v).strip() for v in values if v is not None and str(v).strip()]

    if not non_empty_values:
        return DataType.TEXT

    # Ordered type tests - most specific first
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

    # Test structured types with confidence thresholds
    for test_func, data_type in type_tests:
        match_ratio = test_func(sample_values)
        if match_ratio >= config.type_detection_confidence_threshold:
            return data_type

    # Fallback to string types based on length analysis
    lengths = [len(v) for v in sample_values]
    max_length = max(lengths) if lengths else 0
    if max_length <= 1 and all(len(v) == 1 for v in sample_values):
        return DataType.CHAR
    elif max_length <= config.max_varchar_length:
        return DataType.VARCHAR
    else:
        return DataType.TEXT
