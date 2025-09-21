import logging
from typing import Dict, List

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.schema_analysis.foreign_key.fk_composite import (detect_composite_foreign_keys)
from csv_to_ddl.schema_analysis.foreign_key.fk_map import (build_reference_keys_map)
from csv_to_ddl.schema_analysis.foreign_key.fk_single import (detect_single_column_foreign_keys)
from csv_to_ddl.schema_analysis.models.table import TableSpec


class ForeignKeyAnalyzer:
    def __init__(self):
        self.config = ConfigManager.get_key_config()
        self.logger = logging.getLogger(__name__)

    def analyze_foreign_keys(self, tables_specs: Dict[str, TableSpec],
                             tables_data: Dict[str, List[List[str]]]) -> Dict[str, TableSpec]:
        reference_keys = build_reference_keys_map(tables_specs, tables_data, self.config)

        claimed_relationships = {}
        for table_name, table_spec in tables_specs.items():
            table_spec.foreign_keys = []

            table_data = tables_data.get(table_name, [])
            table_header = reference_keys.get(table_name, {}).get('header', [])

            single_fks = detect_single_column_foreign_keys(table_name, table_header, table_data,
                                                           table_spec, reference_keys, self.config)
            composite_fks = detect_composite_foreign_keys(table_name, table_header, table_data,
                                                           table_spec, reference_keys, self.config)
            all_fks = single_fks + composite_fks

            for fk in all_fks:
                self._claim_relationship(fk, table_name, claimed_relationships)

        for (source_table, winning_fk) in claimed_relationships.values():
            tables_specs[source_table].foreign_keys.append(winning_fk)

        return tables_specs

    @staticmethod
    def _claim_relationship(fk, table_name, claimed_relationships):
        relationship_pair = tuple(sorted([table_name, fk.referenced_table]))

        if relationship_pair not in claimed_relationships:
            claimed_relationships[relationship_pair] = (table_name, fk)
            return

        existing_source, existing_fk = claimed_relationships[relationship_pair]
        if fk.confidence > existing_fk.confidence:
            claimed_relationships[relationship_pair] = (table_name, fk)
