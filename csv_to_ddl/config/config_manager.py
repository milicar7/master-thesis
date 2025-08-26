from typing import Optional

from csv_to_ddl.config.config_provider import ConfigProvider, DefaultConfigProvider
from csv_to_ddl.config.default_config import CSVConfig, KeyConfig, TypeConfig, NormalizationConfig, HeaderConfig


class ConfigManager:
    """Service locator for configuration management"""

    _provider: Optional[ConfigProvider] = None

    @classmethod
    def initialize(cls, provider: ConfigProvider):
        cls._provider = provider

    @classmethod
    def get_csv_config(cls) -> CSVConfig:
        if cls._provider is None:
            cls._provider = DefaultConfigProvider()
        return cls._provider.get_csv_config()

    @classmethod
    def get_header_config(cls) -> HeaderConfig:
        if cls._provider is None:
            cls._provider = DefaultConfigProvider()
        return cls._provider.get_header_config()

    @classmethod
    def get_key_config(cls) -> KeyConfig:
        if cls._provider is None:
            cls._provider = DefaultConfigProvider()
        return cls._provider.get_key_config()

    @classmethod
    def get_type_config(cls) -> TypeConfig:
        if cls._provider is None:
            cls._provider = DefaultConfigProvider()
        return cls._provider.get_type_config()

    @classmethod
    def get_normalization_config(cls) -> NormalizationConfig:
        if cls._provider is None:
            cls._provider = DefaultConfigProvider()
        return cls._provider.get_normalization_config()
