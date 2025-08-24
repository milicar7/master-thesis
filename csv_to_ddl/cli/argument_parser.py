import argparse
from pathlib import Path

from csv_to_ddl.models.dialects import DatabaseDialect


class ArgumentParser:
    """Command line argument parsing for CSV to DDL converter"""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="CSV to DDL converter",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
            Examples:
              %(prog)s -i data/                    # Process all CSV files in directory
              %(prog)s -i file.csv -d mysql        # Convert single file for MySQL
              %(prog)s -i data/ -o schema.sql      # Save DDL to file
              %(prog)s -i data/ --json-report report.json  # Generate detailed analysis report
        """
        )

        parser.add_argument(
            '-i', '--input',
            type=Path,
            required=True,
            help='Input CSV file or directory containing CSV files'
        )

        parser.add_argument(
            '-o', '--output',
            type=Path,
            help='Output file path for DDL (prints to stdout if not specified)'
        )

        parser.add_argument(
            '-r', '--report',
            type=Path,
            help='Path to save detailed JSON analysis report'
        )

        parser.add_argument(
            '-d', '--dialect',
            type=str,
            choices=[d.value for d in DatabaseDialect],
            default=DatabaseDialect.POSTGRESQL.value,
            help='Target database dialect (default: postgresql)'
        )

        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

        return parser
