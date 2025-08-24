import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec


class JsonReporter:
    """Handles generation of detailed JSON analysis outputs"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_report(self, results: Dict[str, Any], output_path: Path) -> None:
        try:
            report = {
                'statistics': self._convert_statistics_to_percentages(results['statistics']),
                'file_metadata': results['file_metadata'],
                'tables': {},
                'normalization_suggestions': []
            }

            JsonReporter._serialize_tables(report, results['tables'])

            JsonReporter._serialize_normalization_suggestions(report, results['normalization_suggestions'])

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"JSON report written to {output_path}")

        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            raise

    @staticmethod
    def _convert_statistics_to_percentages(statistics: Dict[str, Any]) -> Dict[str, Any]:
        converted_stats = statistics.copy()
        
        if 'primary_key_coverage' in converted_stats:
            converted_stats['primary_key_coverage'] = f"{converted_stats['primary_key_coverage']:.1%}"
            
        return converted_stats

    @staticmethod
    def _serialize_tables(report: Dict[str, Any], tables: Dict[str, TableSpec]) -> None:
        for table_name, table_spec in tables.items():
            report['tables'][table_name] = {
                'name': table_spec.name,
                'row_count': table_spec.row_count,
                'column_count': len(table_spec.columns),
                'primary_key': table_spec.primary_key.columns if table_spec.primary_key else None,
                'foreign_key_count': len(table_spec.foreign_keys),
                'columns': JsonReporter._serialize_columns(table_spec.columns),
                'foreign_keys': JsonReporter._serialize_foreign_keys(table_spec.foreign_keys)
            }

    @staticmethod
    def _serialize_columns(columns: List) -> List[Dict[str, Any]]:
        serialized_columns = []
        for col in columns:
            column_data = {
                'name': col.name,
                'data_type': col.data_type.value,
                'nullable': col.nullable,
                'max_length': col.size_spec.max_length,
                'statistics': None
            }
            
            if col.statistics:
                column_data['statistics'] = {
                    'unique_ratio': f"{col.statistics.unique_ratio:.1%}",
                    'null_count': col.statistics.null_count,
                    'distinct_count': col.statistics.distinct_count,
                }
            
            serialized_columns.append(column_data)
        
        return serialized_columns

    @staticmethod
    def _serialize_foreign_keys(foreign_keys: List) -> List[Dict[str, Any]]:
        return [
            {
                'columns': fk.columns,
                'referenced_table': fk.referenced_table,
                'referenced_columns': fk.referenced_columns,
                'confidence': f"{fk.confidence:.1%}",
                'reasoning': fk.reasoning
            }
            for fk in foreign_keys
        ]

    @staticmethod
    def _serialize_normalization_suggestions(report: Dict[str, Any], 
                                           suggestions: List[NormalizationSuggestion]) -> None:
        for suggestion in suggestions:
            report['normalization_suggestions'].append({
                'table_name': suggestion.table_name,
                'suggestion_type': suggestion.suggestion_type,
                'description': suggestion.description,
                'confidence': f"{suggestion.confidence:.1%}"
            })