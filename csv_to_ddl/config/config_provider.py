from typing import Protocol

from csv_to_ddl.config.default_config import CSVConfig, KeyConfig, TypeConfig, NormalizationConfig, HeaderConfig


class ConfigProvider(Protocol):
    """Protocol for configuration providers"""

    def get_csv_config(self) -> CSVConfig:
        ...

    def get_header_config(self) -> HeaderConfig:
        ...

    def get_key_config(self) -> KeyConfig:
        ...

    def get_type_config(self) -> TypeConfig:
        ...

    def get_normalization_config(self) -> NormalizationConfig:
        ...


class DefaultConfigProvider:
    """Default configuration provider using hardcoded defaults"""

    @staticmethod
    def get_csv_config() -> CSVConfig:
        return CSVConfig()

    @staticmethod
    def get_header_config() -> HeaderConfig:
        return HeaderConfig()

    @staticmethod
    def get_key_config() -> KeyConfig:
        return KeyConfig()

    @staticmethod
    def get_type_config() -> TypeConfig:
        return TypeConfig()

    @staticmethod
    def get_normalization_config() -> NormalizationConfig:
        return NormalizationConfig()
