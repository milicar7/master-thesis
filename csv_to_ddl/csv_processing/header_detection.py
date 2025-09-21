import logging
import re
from typing import List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.schema_analysis.columns_and_types.type_detection.type_detectors import is_integer, is_decimal, is_float, is_date, \
    is_datetime
from csv_to_ddl.schema_analysis.columns_and_types.type_detection.type_name import detect_column_type
from csv_to_ddl.schema_analysis.models.dialects import DataType


class HeaderDetection:
    def __init__(self):
        self.header_config = ConfigManager.get_header_config()
        self.type_config = ConfigManager.get_type_config()
        self.logger = logging.getLogger(__name__)

    def has_header(self, rows) -> bool:
        """
        Header detection algorithm using multifactor scoring.
        
        Determines if the first row contains column headers or actual data
        by analyzing multiple characteristics and comparing with data rows.
        
        Process:
        1. Sample first row as potential header and subsequent rows as data
        2. For each potential header cell, calculate composite score:
           - Positive indicators: alphabetic patterns, naming conventions
           - Negative penalties: numeric/date values (less likely to be headers)
           - Type comparison: different types between header and data suggest header row
        3. Apply global adjustments:
           - Uniqueness penalty: headers should be mostly unique
           - Pattern boost: common suffixes like '_id', '_name' increase confidence
        4. Compare final confidence against threshold
        
        Critical for CSV processing as it determines whether to treat first row
        as headers or data, affecting all downstream schema analysis.
        
        Returns:
            True if first row likely contains headers, False if it's data
        """
        if not rows:
            return False

        if len(rows) == 1:
            return True

        first_row = rows[0]
        data_rows = rows[1:min(len(rows), self.header_config.header_data_rows_sample_size)]
        detection_sample_size = min(len(data_rows), self.header_config.header_detection_sample_size)
        header_score = 0.0
        total_cols = len(first_row)

        # Score each potential header cell
        for i, cell in enumerate(first_row):
            col_score = 0.0
            cell = str(cell).strip()
            data_values = []

            if data_rows and i < len(data_rows[0]):
                data_values = [row[i] if i < len(row) else '' for row in data_rows[:detection_sample_size]]

            # Multi-factor scoring
            col_score += self._calculate_header_indicators_score(cell)
            col_score -= self._calculate_anti_header_penalties(cell)
            col_score += self._calculate_type_comparison_score(cell, data_values)

            header_score += max(0.0, min(1.0, col_score))

        # Apply global confidence adjustments
        confidence = header_score / total_cols if total_cols > 0 else 0.0
        confidence *= self._calculate_uniqueness_penalty(first_row)
        confidence += self._calculate_common_pattern_boost(first_row)

        return confidence >= self.header_config.header_confidence_threshold

    def _calculate_header_indicators_score(self, cell: str) -> float:
        col_score = 0.0

        if re.match(r'^[a-zA-Z][a-zA-Z0-9_\s]*$', cell):
            col_score += self.header_config.header_letter_pattern_bonus

        if '_' in cell or ' ' in cell:
            col_score += self.header_config.header_underscore_space_bonus

        if cell.isupper() or cell.islower():
            col_score += self.header_config.header_case_consistency_bonus

        if len(cell) <= self.header_config.header_max_length_threshold:
            col_score += self.header_config.header_length_bonus

        return col_score

    def _calculate_anti_header_penalties(self, cell: str) -> float:
        penalty = 0.0

        int_confidence = is_integer([cell])
        dec_confidence = is_decimal([cell])
        float_confidence = is_float([cell])

        if (int_confidence > self.header_config.header_type_penalty_threshold or
                dec_confidence > self.header_config.header_type_penalty_threshold or
                float_confidence > self.header_config.header_type_penalty_threshold):
            penalty += self.header_config.header_numeric_penalty

        date_confidence = is_date([cell])
        datetime_confidence = is_datetime([cell])

        if (date_confidence > self.header_config.header_type_penalty_threshold or
                datetime_confidence > self.header_config.header_type_penalty_threshold):
            penalty += self.header_config.header_date_penalty

        return penalty

    def _calculate_type_comparison_score(self, cell: str, data_values: List[str]) -> float:
        if not data_values:
            return 0.0

        col_score = 0.0

        header_type = detect_column_type([cell], self.type_config)
        data_type = detect_column_type(data_values, self.type_config)

        if header_type != data_type:
            col_score += self.header_config.header_type_difference_bonus

            if (header_type in [DataType.TEXT, DataType.VARCHAR] and
                    data_type in [DataType.INTEGER, DataType.FLOAT, DataType.DATE,
                                  DataType.DATETIME, DataType.EMAIL, DataType.URL, DataType.UUID]):
                col_score += self.header_config.header_text_vs_structured_bonus

        return col_score

    @staticmethod
    def _calculate_uniqueness_penalty(first_row: List[str]) -> float:
        unique_names = len(set(str(cell).strip().lower() for cell in first_row))
        return unique_names / max(1, len(first_row))

    @staticmethod
    def _calculate_common_pattern_boost(first_row: List[str]) -> float:
        common_suffixes = ['_id', '_key', '_date', '_time', '_at', '_count', '_total', '_name', '_code']
        suffix_matches = sum(1 for cell in first_row if any(str(cell).lower().endswith(suffix)
                                                            for suffix in common_suffixes))
        return (suffix_matches / len(first_row)) * 0.1
