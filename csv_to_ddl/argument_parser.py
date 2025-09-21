import argparse
from pathlib import Path

from csv_to_ddl.schema_analysis.models.dialects import DatabaseDialect


class ArgumentParser:
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="CSV to DDL converter",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
            Examples:
              %(prog)s -i data/                    # Process all CSV files in directory
              %(prog)s -i file.csv -d mysql        # Convert single file for MySQL
              %(prog)s -i data/ -o schema.sql      # Save result to file schema.sql
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
