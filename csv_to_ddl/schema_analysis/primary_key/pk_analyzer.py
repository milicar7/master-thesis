import logging
from typing import List, Tuple, Optional

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.schema_analysis.models.table import TableSpec, ColumnSpec, PrimaryKeySpec
from csv_to_ddl.schema_analysis.primary_key.pk_composite import detect_composite_primary_key
from csv_to_ddl.schema_analysis.primary_key.pk_single import detect_single_key
from csv_to_ddl.schema_analysis.primary_key.pk_surrogate import generate_surrogate_primary_key


class PrimaryKeyAnalyzer:
    def __init__(self):
        self.config = ConfigManager.get_key_config()
        self.logger = logging.getLogger(__name__)

    def analyze_primary_key(self, table_spec: TableSpec,
                            header: List[str], rows: List[List[str]]) -> Tuple[PrimaryKeySpec, Optional[ColumnSpec]]:
        self.logger.debug(f"Analyzing primary key for columns_and_types {table_spec.name}")

        natural_pk = detect_single_key(table_spec, self.config)
        if natural_pk:
            self.logger.info(f"Natural primary key detected for {table_spec.name}: {natural_pk.columns}")
            return natural_pk, None

        composite_pk = detect_composite_primary_key(table_spec, rows, header, self.config)
        if composite_pk:
            self.logger.info(f"Composite primary key detected for {table_spec.name}: {composite_pk.columns}")
            return composite_pk, None

        surrogate_pk, surrogate_column = generate_surrogate_primary_key(table_spec)
        self.logger.info(f"Surrogate primary key generated for {table_spec.name}: {surrogate_pk.columns}")
        return surrogate_pk, surrogate_column
