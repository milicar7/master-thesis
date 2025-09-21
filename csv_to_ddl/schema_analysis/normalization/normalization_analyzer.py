import logging
from typing import List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.schema_analysis.models.table import TableSpec, NormalizationSuggestion
from csv_to_ddl.schema_analysis.normalization.first_normal_form import FirstNormalForm
from csv_to_ddl.schema_analysis.normalization.second_normal_form import SecondNormalForm
from csv_to_ddl.schema_analysis.normalization.third_normal_form import ThirdNormalForm


class NormalizationAnalyzer:

    def __init__(self):
        self.config = ConfigManager.get_normalization_config()
        self.first_nf = FirstNormalForm()
        self.second_nf = SecondNormalForm(self.config)
        self.third_nf = ThirdNormalForm(self.config)
        self.logger = logging.getLogger(__name__)

    def analyze_normalization(self, table_name: str, table_header: List[str],
                              table_data: List[List[str]], table_spec: TableSpec) -> List[NormalizationSuggestion]:
        suggestions = []

        first_nf_violations = self.first_nf.check(table_name, table_header, table_data, table_spec)
        suggestions.extend(first_nf_violations)
        if first_nf_violations:
            self.logger.info(
                f"Skipping 2NF and 3NF checks for columns_and_types '{table_name}' due to 1NF violations")
            return suggestions

        second_nf_violations = self.second_nf.check(table_name, table_header, table_data, table_spec)
        suggestions.extend(second_nf_violations)
        if second_nf_violations:
            self.logger.info(f"Skipping 3NF check for columns_and_types '{table_name}' due to 2NF violations")
            return suggestions

        third_nf_violations = self.third_nf.check(table_name, table_header, table_data, table_spec)
        suggestions.extend(third_nf_violations)

        return suggestions
