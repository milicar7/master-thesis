from dataclasses import dataclass


@dataclass
class NormalizationSuggestion:
    table_name: str
    suggestion_type: str  # "1NF", "2NF", "3NF"
    description: str
    confidence: float = 0.0
