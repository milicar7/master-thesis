from dataclasses import dataclass, field
from typing import List, Optional

from csv_to_ddl.models.dialects import DataType


@dataclass
class ColumnStatistics:
    total_count: int
    null_count: int
    distinct_count: int
    unique_ratio: float
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    sample_values: List[str] = field(default_factory=list)


@dataclass
class ColumnSizeSpec:
    max_length: Optional[int] = None
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
    is_surrogate: bool = False  # Generated surrogate key


@dataclass
class PrimaryKeySpec:
    columns: List[str]
    key_type: str  # "natural", "surrogate", "composite"
    confidence: float = 1.0
    reasoning: str = ""
    is_generated: bool = False  # True if surrogate


@dataclass
class ForeignKeySpec:
    columns: List[str]
    referenced_table: str
    referenced_columns: List[str]
    confidence: float
    match_ratio: float
    reasoning: str


@dataclass
class TableSpec:
    name: str
    columns: List[ColumnSpec]
    primary_key: Optional[PrimaryKeySpec] = None
    foreign_keys: List[ForeignKeySpec] = field(default_factory=list)
    row_count: int = 0
    source_files: List[str] = field(default_factory=list)
