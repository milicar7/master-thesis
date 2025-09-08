import statistics
from typing import List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.schema_analysis.columns_and_types.type_detection.type_name import detect_column_type
from csv_to_ddl.schema_analysis.columns_and_types.type_detection.type_size import calculate_size_spec
from csv_to_ddl.schema_analysis.models.table import ColumnSpec, ColumnStatistics


class ColumnAnalyzer:
    def __init__(self):
        self.type_config = ConfigManager.get_type_config()

    def analyze_column(self, name: str, values: List[str]) -> ColumnSpec:
        """
        Comprehensive column analysis algorithm.
        
        Process:
        1. Calculate statistical properties (null count, uniqueness, lengths)
        2. Detect optimal data type using pattern matching and confidence scoring
        3. Determine size specifications based on data type and actual data
        4. Set nullability based on presence of null/empty values
        
        Combines statistical analysis with pattern recognition to make
        informed decisions about column specifications.
        
        Args:
            name: Column name
            values: All values in the column
            
        Returns:
            Complete column specification with type, size, and constraints
        """
        statistics_obj = self._calculate_statistics(values)
        data_type = detect_column_type(values, self.type_config, statistics_obj)
        size_spec = calculate_size_spec(data_type, statistics_obj.max_length, self.type_config)
        nullable = statistics_obj.null_count > 0

        return ColumnSpec(
            name=name,
            data_type=data_type,
            nullable=nullable,
            size_spec=size_spec,
            statistics=statistics_obj
        )

    @staticmethod
    def _calculate_statistics(values: List[str]) -> ColumnStatistics:
        """
        Calculate comprehensive column statistics for schema inference.
        
        Metrics calculated:
        - Null/empty value count for nullability determination
        - Distinct value count for uniqueness assessment
        - Uniqueness ratio for primary key candidate scoring
        - String length statistics for size specification
        
        These statistics drive type detection, constraint inference,
        and key detection algorithms throughout the system.
        
        Returns:
            ColumnStatistics with all computed metrics
        """
        null_count = sum(1 for v in values if v is None or str(v).strip() == '')
        non_null_values = [str(v).strip() for v in values if v is not None and str(v).strip()]
        distinct_count = len(set(non_null_values))
        unique_ratio = distinct_count / max(1, len(non_null_values))

        lengths = [len(str(v)) for v in non_null_values]
        max_length = max(lengths) if lengths else None
        avg_length = statistics.mean(lengths) if lengths else None

        return ColumnStatistics(
            null_count=null_count,
            distinct_count=distinct_count,
            unique_ratio=unique_ratio,
            max_length=max_length,
            avg_length=avg_length
        )