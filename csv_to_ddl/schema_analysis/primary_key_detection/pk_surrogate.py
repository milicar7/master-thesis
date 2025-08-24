from typing import Tuple

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.models.dialects import DataType
from csv_to_ddl.models.table import TableSpec, ColumnSpec, ColumnStatistics, PrimaryKeySpec


def generate_surrogate_primary_key(table_spec: TableSpec, config: KeyConfig) -> Tuple[PrimaryKeySpec, ColumnSpec]:
    surrogate_name = config.surrogate_key_name
    existing_names = {col.name.lower() for col in table_spec.columns}
    counter = 1
    while surrogate_name.lower() in existing_names:
        surrogate_name = f"{config.surrogate_key_name}_{counter}"
        counter += 1

    surrogate_column = ColumnSpec(name=surrogate_name,
                                  data_type=DataType.INTEGER,
                                  nullable=False,
                                  is_auto_increment=True,
                                  is_surrogate=True,
                                  statistics=ColumnStatistics(total_count=table_spec.row_count,
                                                              null_count=0,
                                                              distinct_count=table_spec.row_count,
                                                              unique_ratio=1.0))

    pk_spec = PrimaryKeySpec(columns=[surrogate_name],
                             key_type="surrogate",
                             confidence=1.0,
                             reasoning=f"Generated surrogate key '{surrogate_name}' - no suitable natural or composite key found",
                             is_generated=True)

    return pk_spec, surrogate_column
