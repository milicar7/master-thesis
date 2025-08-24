import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.csv_processing.csv_reader import find_csv_files, read_csv_file
from csv_to_ddl.csv_processing.header_detection import detect_headers


class CSVAnalyzer:
    """Process CSV files"""

    def __init__(self):
        self.config = ConfigManager.get_csv_config()
        self.type_config = ConfigManager.get_type_config()
        self.logger = logging.getLogger(__name__)

    def process_files(self, input_path: Path) -> Tuple[
        Dict[str, List[List[str]]], Dict[str, List[str]], Dict[str, Any]]:
        files = self._find_and_validate_files(input_path)
        files_data, files_metadata = self._process_all_files(files)
        table_data = self._create_individual_tables(files_data)
        return self._format_output(table_data, files_metadata)

    def _find_and_validate_files(self, input_path: Path) -> List[Path]:
        files = find_csv_files(input_path)
        if not files:
            raise ValueError(f"No CSV files found in {input_path}")

        self.logger.info(f"Found {len(files)} CSV files")
        return files

    def _process_all_files(self, files: List[Path]) -> Tuple[Dict[str, Dict], Dict[str, Any]]:
        files_data = {}
        files_metadata = {}

        for file_path in files:
            try:
                processed_data, metadata = self._process_single_file(file_path)
                if processed_data:
                    files_data[str(file_path)] = processed_data
                    files_metadata[str(file_path)] = metadata
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue

        if not files_data:
            raise ValueError("No valid CSV data found")

        return files_data, files_metadata

    def _process_single_file(self, file_path: Path) -> Tuple[Optional[Dict], Optional[Dict]]:
        rows, metadata = read_csv_file(file_path, self.config)
        if not rows:
            self.logger.warning(f"No data found in {file_path}")
            return None, None

        has_headers, header_confidence = detect_headers(rows, self.config, self.type_config)
        if has_headers:
            headers = [str(h).strip() for h in rows[0]]
            data_rows = rows[1:]
        else:
            headers = [f"column_{i + 1}" for i in range(len(rows[0]) if rows else 0)]
            data_rows = rows

        processed_data = {
            'headers': headers,
            'rows': data_rows,
            'has_headers': has_headers,
            'header_confidence': header_confidence
        }

        return processed_data, metadata

    @staticmethod
    def _create_individual_tables(file_data: Dict[str, Dict]) -> Dict[str, Dict]:
        tables = {}

        for file_path, data in file_data.items():
            table_name = Path(file_path).stem
            tables[table_name] = data

        return tables

    @staticmethod
    def _format_output(table_data: Dict[str, Dict], file_metadata: Dict[str, Any]) -> Tuple[
        Dict[str, List[List[str]]], Dict[str, List[str]], Dict[str, Any]]:
        tables_data = {}
        tables_headers = {}

        for table_name, table_info in table_data.items():
            tables_headers[table_name] = table_info['headers']
            tables_data[table_name] = table_info['rows']

        return tables_data, tables_headers, file_metadata
