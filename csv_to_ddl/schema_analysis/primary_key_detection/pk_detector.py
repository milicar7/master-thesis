import logging
from typing import List, Optional, Tuple

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.models.table import TableSpec, ColumnSpec, PrimaryKeySpec
from csv_to_ddl.schema_analysis.primary_key_detection.pk_composite import detect_composite_primary_key
from csv_to_ddl.schema_analysis.primary_key_detection.pk_single import detect_single_key
from csv_to_ddl.schema_analysis.primary_key_detection.pk_surrogate import generate_surrogate_primary_key


class PrimaryKeyDetector:
    """Handles primary key detection (natural, composite, and surrogate)"""

    def __init__(self):
        self.config = ConfigManager.get_key_config()
        self.logger = logging.getLogger(__name__)

    def detect_primary_key(self, table_spec: TableSpec, rows: List[List[str]], headers: List[str]) -> Tuple[
        Optional[PrimaryKeySpec], Optional[ColumnSpec]]:
        natural_pk = detect_single_key(table_spec, self.config)
        if natural_pk:
            self.logger.info(f"Natural primary key detected for {table_spec.name}: {natural_pk.columns}")
            return natural_pk, None

        if self.config.enable_composite_key_detection:
            composite_pk = detect_composite_primary_key(table_spec, rows, headers, self.config)
            if composite_pk:
                self.logger.info(f"Composite primary key detected for {table_spec.name}: {composite_pk.columns}")
                return composite_pk, None

        if self.config.enable_surrogate_key_generation:
            surrogate_pk, surrogate_column = generate_surrogate_primary_key(table_spec, self.config)
            self.logger.info(f"Surrogate primary key generated for {table_spec.name}: {surrogate_pk.columns}")
            return surrogate_pk, surrogate_column
        else:
            self.logger.warning(f"No primary key could be determined for table {table_spec.name}")
            return None, None
