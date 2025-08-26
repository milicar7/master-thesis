import logging
from typing import Dict, List

from schema_analysis.foreign_key.fk_analyzer import ForeignKeyAnalyzer
from schema_analysis.models.table import TableSpec
from schema_analysis.table_analyzer import TableAnalyzer


class SchemaAnalyzer:
    def __init__(self):
        self.table_analyzer = TableAnalyzer()
        self.foreign_key_analyzer = ForeignKeyAnalyzer()
        self.logger = logging.getLogger(__name__)

    def analyze_tables(self, tables_headers: Dict[str, List[str]],
                       tables_data: Dict[str, List[List[str]]]) -> Dict[str, TableSpec]:
        self.logger.info("Starting columns_and_types analysis")

        tables_specs = {}

        for table_name, rows in tables_data.items():
            header = tables_headers[table_name]

            self.logger.info(f"Analyzing columns_and_types: {table_name}")
            table_spec = self.table_analyzer.analyze_single_table(table_name, header, rows)
            tables_specs[table_name] = table_spec

        self.logger.info("Starting foreign key analysis")
        tables_specs = self.foreign_key_analyzer.analyze_foreign_keys(tables_specs, tables_data)

        return tables_specs
