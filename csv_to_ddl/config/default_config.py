from dataclasses import dataclass

from csv_to_ddl.config.constants.csv import *
from csv_to_ddl.config.constants.foreign_key import *
from csv_to_ddl.config.constants.normalization import *
from csv_to_ddl.config.constants.primary_key import *
from csv_to_ddl.config.constants.type_detection import *


@dataclass
class CSVConfig:
    sample_size: int = SAMPLE_SIZE
    delimiter_detection_sample_size: int = DELIMITER_DETECTION_SAMPLE_SIZE

@dataclass
class HeaderConfig:
    header_detection_sample_size: int = HEADER_DETECTION_SAMPLE_SIZE
    header_data_rows_sample_size: int = HEADER_DATA_ROWS_SAMPLE_SIZE
    header_confidence_threshold: float = HEADER_CONFIDENCE_THRESHOLD
    header_max_length_threshold: int = HEADER_MAX_LENGTH_THRESHOLD
    header_type_penalty_threshold: float = HEADER_TYPE_PENALTY_THRESHOLD

    # Header scoring bonuses
    header_letter_pattern_bonus: float = HEADER_LETTER_PATTERN_BONUS
    header_underscore_space_bonus: float = HEADER_UNDERSCORE_SPACE_BONUS
    header_case_consistency_bonus: float = HEADER_CASE_CONSISTENCY_BONUS
    header_length_bonus: float = HEADER_LENGTH_BONUS
    header_type_difference_bonus: float = HEADER_TYPE_DIFFERENCE_BONUS
    header_text_vs_structured_bonus: float = HEADER_TEXT_VS_STRUCTURED_BONUS

    # Header penalties
    header_numeric_penalty: float = HEADER_NUMERIC_PENALTY
    header_date_penalty: float = HEADER_DATE_PENALTY


@dataclass
class KeyConfig:
    # =============================================================================
    # Surrogate key
    # =============================================================================
    surrogate_key_name: str = "id"

    # =============================================================================
    # Primary Key Detection
    # =============================================================================
    pk_single_confidence_threshold: float = PK_CONFIDENCE_THRESHOLD
    pk_single_uniqueness_threshold: float = PK_SINGLE_UNIQUENESS_THRESHOLD
    pk_composite_uniqueness_threshold: float = PK_COMPOSITE_UNIQUENESS_THRESHOLD

    pk_uniqueness_bonus: float = PK_UNIQUENESS_BONUS
    pk_not_nullable_bonus: float = PK_NOT_NULLABLE_BONUS
    pk_primary_name_bonus: float = PK_PRIMARY_NAME_BONUS
    pk_id_name_bonus: float = PK_ID_NAME_BONUS
    pk_uuid_type_bonus: float = PK_UUID_TYPE_BONUS
    pk_text_length_threshold: int = PK_TEXT_LENGTH_THRESHOLD
    pk_long_text_penalty: float = PK_LONG_TEXT_PENALTY

    pk_composite_size: int = PK_COMPOSITE_SIZE

    # =============================================================================
    # Foreign Key Detection
    # =============================================================================
    fk_overlap_threshold: float = FK_OVERLAP_THRESHOLD

    # Validation bonuses
    fk_validity_bonus: float = FK_VALIDITY_BONUS
    fk_validation_size_bonus: float = FK_VALIDATION_SIZE_BONUS
    fk_validation_overlap_bonus: float = FK_VALIDATION_OVERLAP_BONUS
    fk_validation_threshold: float = FK_VALIDATION_THRESHOLD

    # Naming bonuses
    fk_naming_bonus: float = FK_NAMING_BONUS
    fk_exact_match_bonus: float = FK_EXACT_MATCH_BONUS
    fk_table_prefix_bonus: float = FK_TABLE_PREFIX_BONUS
    fk_table_reference_bonus: float = FK_TABLE_REFERENCE_BONUS
    fk_word_match_bonus: float = FK_WORD_MATCH_BONUS

    # Primary key target bonus
    fk_primary_key_target_bonus: float = FK_PRIMARY_KEY_TARGET_BONUS


@dataclass
class NormalizationConfig:
    # =============================================================================
    # Second Normal Form (2NF) Detection
    # =============================================================================
    nf2_min_rows_for_analysis: int = NF2_MIN_ROWS_FOR_ANALYSIS
    nf2_min_column_values: int = NF2_MIN_COLUMN_VALUES
    nf2_min_unique_keys: int = NF2_MIN_UNIQUE_KEYS
    nf2_partial_dependency_threshold: float = NF2_PARTIAL_DEPENDENCY_THRESHOLD
    nf2_full_key_strength_threshold: float = NF2_FULL_KEY_STRENGTH_THRESHOLD
    nf2_partial_strength_threshold: float = NF2_PARTIAL_STRENGTH_THRESHOLD
    nf2_min_partial_strength: float = NF2_MIN_PARTIAL_STRENGTH

    # =============================================================================
    # Third Normal Form (3NF) Detection
    # =============================================================================
    nf3_min_non_key_columns: int = NF3_MIN_NON_KEY_COLUMNS
    nf3_confidence_threshold: float = NF3_CONFIDENCE_THRESHOLD
    nf3_min_determinant_values: int = NF3_MIN_DETERMINANT_VALUES
    nf3_consistency_penalty: float = NF3_CONSISTENCY_PENALTY
    nf3_base_confidence_high_threshold: float = NF3_BASE_CONFIDENCE_HIGH_THRESHOLD
    nf3_base_confidence_low_threshold: float = NF3_BASE_CONFIDENCE_LOW_THRESHOLD
    nf3_consistency_threshold: float = NF3_CONSISTENCY_THRESHOLD
    nf3_max_uniqueness_bonus: float = NF3_MAX_UNIQUENESS_BONUS
    nf3_uniqueness_bonus_multiplier: float = NF3_UNIQUENESS_BONUS_MULTIPLIER


@dataclass
class TypeConfig:
    type_detection_sample_size: int = TYPE_DETECTION_SAMPLE_SIZE
    type_detection_confidence_threshold: float = TYPE_DETECTION_CONFIDENCE_THRESHOLD

    max_varchar_length: int = MAX_VARCHAR_LENGTH
    uuid_char_length: int = UUID_CHAR_LENGTH
    boolean_length: int = BOOLEAN_LENGTH

    decimal_precision_limit: int = DECIMAL_PRECISION_LIMIT
    decimal_scale_limit: int = DECIMAL_SCALE_LIMIT