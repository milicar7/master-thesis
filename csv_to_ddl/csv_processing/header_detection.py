import re
from typing import List, Tuple

from csv_to_ddl.config.default_config import CSVConfig, TypeConfig
from csv_to_ddl.models.dialects import DataType
from csv_to_ddl.schema_analysis.type_detection.type_name import (detect_column_type, is_date, is_datetime, is_integer,
                                                                 is_decimal,
                                                                 is_float)


def calculate_header_indicators_score(cell_str: str, config: CSVConfig) -> float:
    col_score = 0.0

    if re.match(r'^[a-zA-Z][a-zA-Z0-9_\s]*$', cell_str):
        col_score += config.header_letter_pattern_bonus

    if '_' in cell_str or ' ' in cell_str:
        col_score += config.header_underscore_space_bonus

    if cell_str.isupper() or cell_str.islower():
        col_score += config.header_case_consistency_bonus

    if len(cell_str) <= config.header_max_length_threshold:
        col_score += config.header_length_bonus

    return col_score


def calculate_anti_header_penalties(cell_str: str, config: CSVConfig) -> float:
    penalty = 0.0

    int_confidence, _ = is_integer([cell_str])
    dec_confidence, _ = is_decimal([cell_str])
    float_confidence, _ = is_float([cell_str])
    
    if (int_confidence > config.header_type_penalty_threshold or 
        dec_confidence > config.header_type_penalty_threshold or 
        float_confidence > config.header_type_penalty_threshold):
        penalty += config.header_numeric_penalty

    date_confidence, _ = is_date([cell_str])
    datetime_confidence, _ = is_datetime([cell_str])
    
    if (date_confidence > config.header_type_penalty_threshold or 
        datetime_confidence > config.header_type_penalty_threshold):
        penalty += config.header_date_penalty

    return penalty


def calculate_type_comparison_score(cell_str: str, data_values: List[str], config: CSVConfig, type_config: TypeConfig) -> float:
    if not data_values:
        return 0.0

    col_score = 0.0

    header_type, header_metadata = detect_column_type([cell_str], type_config)
    data_type, data_metadata = detect_column_type(data_values, type_config)

    if header_type != data_type:
        col_score += config.header_type_difference_bonus

        if (header_type in [DataType.TEXT, DataType.VARCHAR] and
                data_type in [DataType.INTEGER, DataType.FLOAT, DataType.DATE,
                              DataType.DATETIME, DataType.EMAIL, DataType.URL, DataType.UUID]):
            col_score += config.header_text_vs_structured_bonus

    header_confidence = header_metadata.get('match_ratio', 0.5)
    data_confidence = data_metadata.get('match_ratio', 0.5)

    if data_confidence > 0.9 and header_confidence < 0.5:
        col_score += config.header_confidence_contrast_bonus

    return col_score


def calculate_uniqueness_penalty(first_row: List[str]) -> float:
    unique_names = len(set(str(cell).strip().lower() for cell in first_row))
    return unique_names / max(1, len(first_row))


def calculate_common_pattern_boost(first_row: List[str]) -> float:
    common_suffixes = ['_id', '_key', '_date', '_time', '_at', '_count', '_total', '_name', '_code']
    suffix_matches = sum(
        1 for cell in first_row if any(str(cell).lower().endswith(suffix) for suffix in common_suffixes))
    return (suffix_matches / len(first_row)) * 0.1


def calculate_column_score(cell: str, data_values: List[str], config: CSVConfig, type_config: TypeConfig) -> float:
    cell_str = str(cell).strip()
    col_score = 0.0

    col_score += calculate_header_indicators_score(cell_str, config)
    col_score -= calculate_anti_header_penalties(cell_str, config)
    col_score += calculate_type_comparison_score(cell_str, data_values, config, type_config)

    return max(0.0, min(1.0, col_score))


def detect_headers(rows: List[List[str]], config: CSVConfig, type_config: TypeConfig) -> Tuple[bool, float]:
    if not rows:
        return False, 0.0

    if len(rows) == 1:
        return True, 0.5

    first_row = rows[0]
    if not first_row:
        return False, 0.0

    data_rows = rows[1:min(len(rows), config.header_data_rows_sample_size)]
    header_score = 0.0
    total_cols = len(first_row)

    for i, cell in enumerate(first_row):
        data_values = []
        if data_rows and i < len(data_rows[0]):
            data_values = [row[i] if i < len(row) else '' for row in
                           data_rows[:min(len(data_rows), config.header_detection_sample_size)]]

        col_score = calculate_column_score(cell, data_values, config, type_config)
        header_score += col_score

    confidence = header_score / total_cols if total_cols > 0 else 0.0
    confidence *= calculate_uniqueness_penalty(first_row)
    confidence += calculate_common_pattern_boost(first_row)

    has_headers = confidence >= config.header_confidence_threshold
    return has_headers, confidence
