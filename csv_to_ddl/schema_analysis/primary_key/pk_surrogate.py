from typing import Tuple

from csv_to_ddl.schema_analysis.models.dialects import DataType
from csv_to_ddl.schema_analysis.models.table import TableSpec, ColumnSpec, ColumnStatistics, PrimaryKeySpec


def generate_surrogate_primary_key(table_spec: TableSpec) -> Tuple[PrimaryKeySpec, ColumnSpec]:
    surrogate_name = f"{table_spec.name}_id"
    existing_names = {col.name.lower() for col in table_spec.columns}
    counter = 1
    while surrogate_name.lower() in existing_names:
        surrogate_name = f"{table_spec.name}_id_{counter}"
        counter += 1

    surrogate_column = ColumnSpec(name=surrogate_name,
                                  data_type=DataType.INTEGER,
                                  nullable=False,
                                  is_auto_increment=True,
                                  statistics=ColumnStatistics(null_count=0,
                                                              distinct_count=table_spec.row_count,
                                                              unique_ratio=1.0))

    pk_spec = PrimaryKeySpec(columns=[surrogate_name],
                             key_type="surrogate")

    return pk_spec, surrogate_column
