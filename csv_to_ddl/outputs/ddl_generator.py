import logging
from datetime import datetime
from typing import Dict

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.models.dialects import DIALECT_CONFIGS, DatabaseDialect
from csv_to_ddl.models.table import TableSpec, ColumnSpec, ForeignKeySpec
from csv_to_ddl.schema_analysis.type_detection.type_size import format_type_with_size


class DDLGenerator:
    """Generate DDL statements for different database dialects"""

    def __init__(self, dialect: DatabaseDialect):
        self.dialect = dialect
        self.config = DIALECT_CONFIGS[dialect]
        self.type_config = ConfigManager.get_type_config()
        self.logger = logging.getLogger(__name__)

    def generate_schema_ddl(self, tables_specs: Dict[str, TableSpec]) -> str:
        ddl_parts = [f"-- Generated DDL for {self.dialect.value}", f"-- Generated at: {datetime.now().isoformat()}", ""]

        for table_name, table_spec in tables_specs.items():
            table_ddl = self._generate_table_ddl(table_spec)
            ddl_parts.append(table_ddl)
            ddl_parts.append("")

        return "\n".join(ddl_parts)

    def _generate_table_ddl(self, table_spec: TableSpec) -> str:
        lines = [f"CREATE TABLE {self._quote_identifier(table_spec.name)} ("]

        column_lines = []
        for col in table_spec.columns:
            col_ddl = self._generate_column_ddl(col)
            column_lines.append(f"    {col_ddl}")

        pk_columns = table_spec.primary_key.columns if table_spec.primary_key else None
        if pk_columns:
            pk_cols = ", ".join(self._quote_identifier(col) for col in pk_columns)
            column_lines.append(f"    PRIMARY KEY ({pk_cols})")

        for fk in table_spec.foreign_keys:
            fk_ddl = self._generate_foreign_key_ddl(fk)
            column_lines.append(f"    {fk_ddl}")

        lines.append(",\n".join(column_lines))
        lines.append(");")

        return "\n".join(lines)

    def _generate_column_ddl(self, col: ColumnSpec) -> str:
        parts = [self._quote_identifier(col.name)]

        sql_type = format_type_with_size(col.data_type, col.size_spec, self.dialect, self.type_config)

        parts.append(sql_type)

        if col.is_auto_increment:
            if self.config.auto_increment_syntax:
                parts.append(self.config.auto_increment_syntax)

        if not col.nullable:
            parts.append("NOT NULL")

        return " ".join(parts)

    def _generate_foreign_key_ddl(self, fk: ForeignKeySpec) -> str:
        fk_cols = ", ".join(self._quote_identifier(col) for col in fk.columns)
        ref_cols = ", ".join(self._quote_identifier(col) for col in fk.referenced_columns)

        return (f"FOREIGN KEY ({fk_cols}) "
                f"REFERENCES {self._quote_identifier(fk.referenced_table)} ({ref_cols})")

    def _quote_identifier(self, identifier: str) -> str:
        return f"{self.config.quote_char}{identifier}{self.config.quote_char}"
