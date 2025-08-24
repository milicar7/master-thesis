from dataclasses import dataclass
from enum import Enum
from typing import Dict


class DataType(Enum):
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    DECIMAL = "DECIMAL"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    UUID = "UUID"
    EMAIL = "EMAIL"
    URL = "URL"
    JSON = "JSON"
    TEXT = "TEXT"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"


class DatabaseDialect(Enum):
    """Supported database dialects"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQL_SERVER = "sqlserver"


@dataclass
class DialectConfig:
    """Configuration for database dialect-specific mappings"""
    type_mappings: Dict[DataType, str]
    quote_char: str = '"'
    auto_increment_syntax: str = ""
    supports_uuid: bool = True
    supports_json: bool = True
    boolean_needs_size: bool = False

DIALECT_CONFIGS = {
    DatabaseDialect.SQLITE: DialectConfig(
        type_mappings={
            DataType.INTEGER: "INTEGER",
            DataType.BIGINT: "INTEGER",
            DataType.DECIMAL: "REAL",
            DataType.FLOAT: "REAL",
            DataType.BOOLEAN: "INTEGER",
            DataType.DATE: "TEXT",
            DataType.TIME: "TEXT",
            DataType.DATETIME: "TEXT",
            DataType.TIMESTAMP: "TEXT",
            DataType.UUID: "TEXT",
            DataType.EMAIL: "TEXT",
            DataType.URL: "TEXT",
            DataType.JSON: "TEXT",
            DataType.TEXT: "TEXT",
            DataType.VARCHAR: "TEXT",
            DataType.CHAR: "TEXT",
        },
        auto_increment_syntax="AUTOINCREMENT",
        supports_uuid=False,
        supports_json=False,
    ),
    DatabaseDialect.POSTGRESQL: DialectConfig(
        type_mappings={
            DataType.INTEGER: "INTEGER",
            DataType.BIGINT: "BIGINT",
            DataType.DECIMAL: "DECIMAL",
            DataType.FLOAT: "DOUBLE PRECISION",
            DataType.BOOLEAN: "BOOLEAN",
            DataType.DATE: "DATE",
            DataType.TIME: "TIME",
            DataType.DATETIME: "TIMESTAMP",
            DataType.TIMESTAMP: "TIMESTAMP",
            DataType.UUID: "UUID",
            DataType.EMAIL: "VARCHAR",
            DataType.URL: "TEXT",
            DataType.JSON: "JSONB",
            DataType.TEXT: "TEXT",
            DataType.VARCHAR: "VARCHAR",
            DataType.CHAR: "CHAR",
        },
        auto_increment_syntax="SERIAL"
    ),
    DatabaseDialect.MYSQL: DialectConfig(
        type_mappings={
            DataType.INTEGER: "INT",
            DataType.BIGINT: "BIGINT",
            DataType.DECIMAL: "DECIMAL",
            DataType.FLOAT: "DOUBLE",
            DataType.BOOLEAN: "TINYINT",
            DataType.DATE: "DATE",
            DataType.TIME: "TIME",
            DataType.DATETIME: "DATETIME",
            DataType.TIMESTAMP: "TIMESTAMP",
            DataType.UUID: "CHAR",
            DataType.EMAIL: "VARCHAR",
            DataType.URL: "TEXT",
            DataType.JSON: "JSON",
            DataType.TEXT: "TEXT",
            DataType.VARCHAR: "VARCHAR",
            DataType.CHAR: "CHAR",
        },
        quote_char="`",
        auto_increment_syntax="AUTO_INCREMENT",
        supports_uuid=False,
        boolean_needs_size=True,
    ),
    DatabaseDialect.SQL_SERVER: DialectConfig(
        type_mappings={
            DataType.INTEGER: "INT",
            DataType.BIGINT: "BIGINT",
            DataType.DECIMAL: "DECIMAL",
            DataType.FLOAT: "FLOAT",
            DataType.BOOLEAN: "BIT",
            DataType.DATE: "DATE",
            DataType.TIME: "TIME",
            DataType.DATETIME: "DATETIME2",
            DataType.TIMESTAMP: "DATETIME2",
            DataType.UUID: "UNIQUEIDENTIFIER",
            DataType.EMAIL: "NVARCHAR",
            DataType.URL: "NVARCHAR(MAX)",
            DataType.JSON: "NVARCHAR(MAX)",
            DataType.TEXT: "NVARCHAR(MAX)",
            DataType.VARCHAR: "NVARCHAR",
            DataType.CHAR: "NCHAR",
        },
        quote_char="[",
        auto_increment_syntax="IDENTITY(1,1)",
        supports_json=False,
    ),
}
