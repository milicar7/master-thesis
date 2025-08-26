import logging
from pathlib import Path
from typing import Dict, List, Tuple

from csv_processing.header_detection import HeaderDetection
from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.csv_processing.csv_helpers import find_csv_files, read_csv_file


class CSVAnalyzer:
    def __init__(self):
        self.csv_config = ConfigManager.get_csv_config()
        self.header_detection = HeaderDetection()
        self.logger = logging.getLogger(__name__)

    def process(self, input_path: Path) -> Tuple[Dict[str, List[str]], Dict[str, List[List[str]]]]:
        files = find_csv_files(input_path)
        if not files:
            raise ValueError(f"No CSV files found in {input_path}")

        files_data = {}
        for file_path in files:
            try:
                rows = read_csv_file(file_path, self.csv_config.sample_size,
                                     self.csv_config.delimiter_detection_sample_size)
                if not rows:
                    self.logger.warning(f"No data found in {file_path}, skipping it")
                else:
                    csv_data = self.get_header_and_data(rows)
                    if csv_data:
                        files_data[str(file_path)] = csv_data
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue

        if not files_data:
            raise ValueError("No valid CSV data found")

        return self.create_individual_tables(files_data)

    def get_header_and_data(self, rows: List[List[str]]) -> Dict[str, List[str]]:
        if self.header_detection.has_headers(rows):
            header = [str(h).strip() for h in rows[0]]
            data_rows = rows[1:]
        else:
            header = [f"column_{i + 1}" for i in range(len(rows[0]) if rows else 0)]
            data_rows = rows

        return {'header': header, 'rows': data_rows}

    @staticmethod
    def create_individual_tables(files_data: Dict[str, Dict[str, List[str]]]) -> Tuple[
        Dict[str, List[str]], Dict[str, List[List[str]]]]:
        tables = {}
        for file_path, data in files_data.items():
            table_name = Path(file_path).stem
            tables[table_name] = data

        tables_headers = {}
        tables_data = {}
        for table_name, table_info in tables.items():
            tables_headers[table_name] = table_info['header']
            tables_data[table_name] = table_info['rows']

        return tables_headers, tables_data
