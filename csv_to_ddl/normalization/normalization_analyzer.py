import logging
from typing import Dict, List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.models.normalization import NormalizationSuggestion
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.normalization.first_normal_form import FirstNormalForm
from csv_to_ddl.normalization.second_normal_form import SecondNormalForm
from csv_to_ddl.normalization.third_normal_form import ThirdNormalForm


class NormalizationAnalyzer:

    def __init__(self):
        self.config = ConfigManager.get_normalization_config()
        self.first_nf = FirstNormalForm()
        self.second_nf = SecondNormalForm(self.config)
        self.third_nf = ThirdNormalForm(self.config)
        self.logger = logging.getLogger(__name__)

    def analyze(self, table_specs: Dict[str, TableSpec],
                tables_data: Dict[str, List[List[str]]],
                tables_headers: Dict[str, List[str]]) -> List[NormalizationSuggestion]:
        suggestions = []

        for table_name, table_spec in table_specs.items():
            table_data = tables_data.get(table_name, [])
            table_headers = tables_headers.get(table_name, [])
            
            if not table_data or not table_headers:
                self.logger.warning(f"No data found for table {table_name}")
                continue

            first_nf_violations = self.first_nf.check(table_name, table_data, table_headers)
            suggestions.extend(first_nf_violations)

            if not first_nf_violations:
                second_nf_violations = self.second_nf.check(table_name, table_data, table_headers, table_spec)
                suggestions.extend(second_nf_violations)

                if not second_nf_violations:
                    third_nf_violations = self.third_nf.check(table_name, table_data, table_headers, table_spec)
                    suggestions.extend(third_nf_violations)
                else:
                    self.logger.info(f"Skipping 3NF check for table '{table_name}' due to 2NF violations")
            else:
                self.logger.info(f"Skipping 2NF and 3NF checks for table '{table_name}' due to 1NF violations")

        return suggestions

