import logging
from pathlib import Path
from typing import Dict, List, Any, Counter

from csv_to_ddl.csv_processing.csv_analyzer import CSVAnalyzer
from csv_to_ddl.models.dialects import DatabaseDialect
from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.normalization.normalization_analyzer import NormalizationAnalyzer
from csv_to_ddl.outputs.ddl_generator import DDLGenerator
from csv_to_ddl.schema_analysis.schema_analyzer import SchemaAnalyzer


class CSVToDDLConverter:
    """Main application class"""

    def __init__(self):
        self.csv_analyzer = CSVAnalyzer()
        self.schema_analyzer = SchemaAnalyzer()
        self.normalization_analyzer = NormalizationAnalyzer()
        self.logger = logging.getLogger(__name__)

    def convert(self, input_path: Path,
                dialect: DatabaseDialect = DatabaseDialect.POSTGRESQL) -> Dict[str, Any]:
        self.logger.info(f"Starting conversion of {input_path}")

        tables_data, tables_headers, file_metadata = self.csv_analyzer.process_files(input_path)

        table_specs = self.schema_analyzer.analyze_tables(tables_data, tables_headers)

        ddl_generator = DDLGenerator(dialect)
        ddl = ddl_generator.generate_schema_ddl(table_specs)

        normalization_suggestions = self.normalization_analyzer.analyze(table_specs, tables_data, tables_headers)

        results = {
            'ddl': ddl,
            'tables': table_specs,
            'normalization_suggestions': normalization_suggestions,
            'file_metadata': file_metadata,
            'statistics': self._compile_statistics(table_specs, normalization_suggestions)
        }

        return results

    def output_ddl(self, output, results):
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(results['ddl'])
            self.logger.info(f"DDL written to {output}")
        else:
            print(results['ddl'])

    @staticmethod
    def _compile_statistics(table_specs: Dict[str, TableSpec],
                            suggestions: List[NormalizationSuggestion]) -> Dict[str, Any]:
        total_tables = len(table_specs)
        total_columns = sum(len(spec.columns) for spec in table_specs.values())
        total_foreign_keys = sum(len(spec.foreign_keys) for spec in table_specs.values())

        tables_with_pk = sum(1 for spec in table_specs.values() if spec.primary_key)

        type_distribution = Counter()
        for spec in table_specs.values():
            for col in spec.columns:
                type_distribution[col.data_type.value] += 1

        return {
            'total_tables': total_tables,
            'total_columns': total_columns,
            'total_foreign_keys': total_foreign_keys,
            'tables_with_primary_key': tables_with_pk,
            'primary_key_coverage': tables_with_pk / max(1, total_tables),
            'data_type_distribution': dict(type_distribution),
            'normalization_suggestions_count': len(suggestions),
            'normalization_suggestions_by_type': Counter(s.suggestion_type for s in suggestions)
        }
