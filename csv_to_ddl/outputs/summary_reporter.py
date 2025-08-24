import logging
from collections import Counter
from typing import Dict, Any


class SummaryReporter:
    """Handles printing conversion summary statistics"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def print_summary(self, results: Dict[str, Any]) -> None:
        stats = results['statistics']

        self.logger.info("=" * 50)
        self.logger.info("CONVERSION SUMMARY")
        self.logger.info("=" * 50)

        self._print_basic_stats(stats)

        self._print_normalization_stats(stats)

        self._print_data_type_stats(stats)

        self.logger.info("Conversion completed successfully!")

    def _print_basic_stats(self, stats: Dict[str, Any]) -> None:
        self.logger.info(f"Tables created: {stats['total_tables']}")
        self.logger.info(f"Total columns: {stats['total_columns']}")
        self.logger.info(f"Primary key coverage: {stats['primary_key_coverage']:.1%}")
        self.logger.info(f"Foreign keys detected: {stats['total_foreign_keys']}")

    def _print_normalization_stats(self, stats: Dict[str, Any]) -> None:
        if stats['normalization_suggestions_count'] > 0:
            self.logger.info(f"Normalization suggestions: {stats['normalization_suggestions_count']}")
            for norm_type, count in stats['normalization_suggestions_by_type'].items():
                self.logger.info(f"  {norm_type}: {count}")

    def _print_data_type_stats(self, stats: Dict[str, Any]) -> None:
        self.logger.info("Top data types:")
        for dtype, count in Counter(stats['data_type_distribution']).most_common(5):
            self.logger.info(f"  {dtype}: {count}")
