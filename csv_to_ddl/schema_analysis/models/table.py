from dataclasses import dataclass, field
from typing import List, Optional

from csv_to_ddl.schema_analysis.models.dialects import DataType


@dataclass
class ColumnStatistics:
    null_count: int
    distinct_count: int
    unique_ratio: float
    max_length: Optional[int] = None
    avg_length: Optional[float] = None


@dataclass
class ColumnSizeSpec:
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None


@dataclass
class ColumnSpec:
    name: str
    data_type: DataType
    nullable: bool
    size_spec: ColumnSizeSpec = field(default_factory=ColumnSizeSpec)
    statistics: Optional[ColumnStatistics] = None
    is_auto_increment: bool = False  # For surrogate keys


@dataclass
class PrimaryKeySpec:
    columns: List[str]
    key_type: str  # "natural", "surrogate", "composite"


@dataclass
class ForeignKeySpec:
    columns: List[str]
    referenced_table: str
    referenced_columns: List[str]
    confidence: float


@dataclass
class NormalizationSuggestion:
    table_name: str
    suggestion_type: str  # "1NF", "2NF", "3NF"
    description: str
    confidence: float = 0.0


@dataclass
class TableSpec:
    name: str
    columns: List[ColumnSpec] = field(default_factory=list)
    row_count: int = 0
    primary_key: Optional[PrimaryKeySpec] = None
    normalization_suggestions: List[NormalizationSuggestion] = field(default_factory=list)
    foreign_keys: List[ForeignKeySpec] = field(default_factory=list)
