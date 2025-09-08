import logging
from pathlib import Path

from csv_to_ddl.csv_processing.csv_analyzer import CSVAnalyzer
from csv_to_ddl.schema_analysis.schema_analyzer import SchemaAnalyzer
from ddl_generator import DDLGenerator
from schema_analysis.models.dialects import DatabaseDialect


class CSVToDDLConverter:
    def __init__(self, dialect: DatabaseDialect = DatabaseDialect.POSTGRESQL):
        self.csv_analyzer = CSVAnalyzer()
        self.schema_analyzer = SchemaAnalyzer()
        self.ddl_generator = DDLGenerator(dialect)
        self.logger = logging.getLogger(__name__)

    def convert(self, input_path: Path) -> str:
        self.logger.info(f"Starting conversion of {input_path}")

        tables_headers, tables_data = self.csv_analyzer.process(input_path)
        tables_specs = self.schema_analyzer.analyze_tables(tables_headers, tables_data)
        return self.ddl_generator.generate_schema_ddl(tables_specs)

    def write_output(self, output, result):
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            self.logger.info(f"Result written to {output}")
        else:
            print(result)
