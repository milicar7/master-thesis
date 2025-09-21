import logging
from typing import List

from csv_to_ddl.schema_analysis.columns_and_types.column_analyzer import ColumnAnalyzer
from csv_to_ddl.schema_analysis.models.table import TableSpec
from csv_to_ddl.schema_analysis.normalization.normalization_analyzer import NormalizationAnalyzer
from csv_to_ddl.schema_analysis.primary_key.pk_analyzer import PrimaryKeyAnalyzer


class TableAnalyzer:
    def __init__(self):
        self.column_analyzer = ColumnAnalyzer()
        self.primary_key_analyzer = PrimaryKeyAnalyzer()
        self.normalization_analyzer = NormalizationAnalyzer()
        self.logger = logging.getLogger(__name__)

    def analyze_single_table(self, table_name: str, header: List[str], rows: List[List[str]]) -> TableSpec:
        if header and rows:
            max_cols = max(len(header), max(len(row) for row in rows) if rows else 0)
            column_data = [[] for _ in range(max_cols)]

            for row in rows:
                for i in range(max_cols):
                    value = row[i] if i < len(row) else ''
                    column_data[i].append(value)
        else:
            column_data = [[] for _ in header]

        columns = []
        for i, col_name in enumerate(header):
            values = column_data[i] if i < len(column_data) else []
            column_spec = self.column_analyzer.analyze_column(col_name, values)
            columns.append(column_spec)

        table_spec = TableSpec(name=table_name, columns=columns, row_count=len(rows))

        primary_key, surrogate_column = self.primary_key_analyzer.analyze_primary_key(table_spec, header, rows)
        table_spec.primary_key = primary_key
        if surrogate_column:
            table_spec.columns.append(surrogate_column)

        normalization_suggestions = self.normalization_analyzer.analyze_normalization(table_name, header, rows, table_spec)
        table_spec.normalization_suggestions.extend(normalization_suggestions)

        return table_spec
