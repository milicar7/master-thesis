import logging
from typing import Dict, List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.models.table import TableSpec
from csv_to_ddl.schema_analysis.foreign_key_detection.fk_composite import (detect_composite_foreign_keys)
from csv_to_ddl.schema_analysis.foreign_key_detection.fk_map import (build_reference_keys_map)
from csv_to_ddl.schema_analysis.foreign_key_detection.fk_single import (detect_single_column_foreign_keys)


class ForeignKeyDetector:

    def __init__(self):
        self.config = ConfigManager.get_key_config()
        self.logger = logging.getLogger(__name__)

    def detect_foreign_keys(self, table_specs: Dict[str, TableSpec],
                            tables_data: Dict[str, List[List[str]]]) -> None:
        reference_keys = build_reference_keys_map(table_specs, tables_data, self.config)
        claimed_relationships = {}

        for table_name, table_spec in table_specs.items():
            table_spec.foreign_keys = []

            single_fks = detect_single_column_foreign_keys(table_name, table_spec, reference_keys, tables_data, self.config)
            composite_fks = detect_composite_foreign_keys(table_name, table_spec, reference_keys, tables_data, self.config)
            all_fks = single_fks + composite_fks

            for fk in all_fks:
                relationship_pair = tuple(sorted([table_name, fk.referenced_table]))

                if relationship_pair in claimed_relationships:
                    existing_source, existing_fk = claimed_relationships[relationship_pair]
                    if fk.confidence > existing_fk.confidence:
                        claimed_relationships[relationship_pair] = (table_name, fk)
                else:
                    claimed_relationships[relationship_pair] = (table_name, fk)

        for (source_table, winning_fk) in claimed_relationships.values():
            table_specs[source_table].foreign_keys.append(winning_fk)
