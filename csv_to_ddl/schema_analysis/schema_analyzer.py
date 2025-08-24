import logging
import statistics
from typing import Dict, List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.models.table import TableSpec, ColumnSpec, ColumnStatistics
from csv_to_ddl.schema_analysis.foreign_key_detection.fk_detector import ForeignKeyDetector
from csv_to_ddl.schema_analysis.primary_key_detection.pk_detector import PrimaryKeyDetector
from csv_to_ddl.schema_analysis.type_detection.type_name import detect_column_type
from csv_to_ddl.schema_analysis.type_detection.type_size import calculate_size_spec


class SchemaAnalyzer:
    """Main schema analysis orchestrator"""

    def __init__(self):
        self.type_config = ConfigManager.get_type_config()
        self.primary_key_detector = PrimaryKeyDetector()
        self.foreign_key_detector = ForeignKeyDetector()
        self.logger = logging.getLogger(__name__)

    def analyze_tables(self, tables_data: Dict[str, List[List[str]]],
                       tables_headers: Dict[str, List[str]]) -> Dict[str, TableSpec]:
        table_specs = {}

        for table_name, rows in tables_data.items():
            headers = tables_headers.get(table_name, [])
            if not headers:
                self.logger.warning(f"No headers found for table {table_name}")
                continue

            self.logger.info(f"Analyzing table: {table_name}")
            table_spec = self._analyze_single_table(table_name, headers, rows)
            table_specs[table_name] = table_spec

        self.foreign_key_detector.detect_foreign_keys(table_specs, tables_data)

        return table_specs

    def _analyze_single_table(self, table_name: str, headers: List[str],
                              rows: List[List[str]]) -> TableSpec:
        columns = []

        if rows and headers:
            max_cols = max(len(headers), max(len(row) for row in rows) if rows else 0)
            column_data = [[] for _ in range(max_cols)]

            for row in rows:
                for i in range(max_cols):
                    value = row[i] if i < len(row) else ''
                    column_data[i].append(value)
        else:
            column_data = [[] for _ in headers]

        for i, header in enumerate(headers):
            if i < len(column_data):
                values = column_data[i]
            else:
                values = []

            column_spec = self._analyze_column(header, values)
            columns.append(column_spec)

        table_spec = TableSpec(
            name=table_name,
            columns=columns,
            row_count=len(rows)
        )

        primary_key, surrogate_column = self.primary_key_detector.detect_primary_key(table_spec, rows, headers)
        table_spec.primary_key = primary_key
        if surrogate_column:
            table_spec.columns.append(surrogate_column)

        return table_spec

    def _analyze_column(self, name: str, values: List[str]) -> ColumnSpec:
        total_count = len(values)
        null_count = sum(1 for v in values if v is None or str(v).strip() == '')
        non_null_values = [str(v).strip() for v in values if v is not None and str(v).strip()]
        distinct_count = len(set(non_null_values))
        unique_ratio = distinct_count / max(1, len(non_null_values))

        lengths = [len(str(v)) for v in non_null_values]
        min_length = min(lengths) if lengths else None
        max_length = max(lengths) if lengths else None
        avg_length = statistics.mean(lengths) if lengths else None

        sample_values = non_null_values[:min(10, len(non_null_values))]

        statistics_obj = ColumnStatistics(
            total_count=total_count,
            null_count=null_count,
            distinct_count=distinct_count,
            unique_ratio=unique_ratio,
            min_length=min_length,
            max_length=max_length,
            avg_length=avg_length,
            sample_values=sample_values
        )

        data_type, type_metadata = detect_column_type(non_null_values, self.type_config)
        size_spec = calculate_size_spec(data_type, type_metadata, self.type_config)

        nullable = null_count > 0

        return ColumnSpec(
            name=name,
            data_type=data_type,
            nullable=nullable,
            size_spec=size_spec,
            statistics=statistics_obj
        )
