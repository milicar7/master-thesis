import csv
import gzip
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

from csv_to_ddl.config.default_config import CSVConfig

logger = logging.getLogger(__name__)


def find_csv_files(path: Path) -> List[Path]:
    if path.is_file():
        if path.suffix.lower() == '.csv' or path.name.endswith('.csv.gz'):
            return [path]
        return []

    csv_files = []
    try:
        csv_files.extend(path.rglob("*.csv"))
        csv_files.extend(path.rglob("*.CSV"))
        csv_files.extend(path.rglob("*.csv.gz"))
    except PermissionError as e:
        logger.warning(f"Permission denied accessing {path}: {e}")

    return csv_files


def _clean_csv_cell(cell: str) -> str:
    """Clean CSV cell by removing BOM and other problematic Unicode characters"""
    if not cell:
        return cell
    
    # Remove BOM characters
    cell = cell.lstrip('\ufeff\ufffe\u200b')
    
    # Replace non-breaking spaces with regular spaces
    cell = cell.replace('\u00a0', ' ')
    
    return cell.strip()


def read_csv_file(file_path: Path, config: CSVConfig) -> Tuple[List[List[str]], Dict[str, Any]]:
    rows = []
    encoding = None
    delimiter = ','
    metadata = {'file_path': str(file_path), 'sample_method': 'sequential'}
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for enc in encodings_to_try:
        try:
            with _open_file(file_path, encoding=enc) as f:
                all_lines = [line for line in (f.readline() for _ in range(config.sample_size)) if line]

                if all_lines:
                    sample_text = ''.join(all_lines[:config.delimiter_detection_sample_size])
                    try:
                        sniffer = csv.Sniffer()
                        delimiter = sniffer.sniff(sample_text).delimiter
                    except Exception:
                        delimiter = ','

                    reader = csv.reader(all_lines, delimiter=delimiter)
                    raw_rows = list(reader)
                    rows = [[_clean_csv_cell(cell) for cell in row] for row in raw_rows]

                    encoding = enc
                    break

        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error sampling {file_path} with encoding {enc}: {e}")
            continue

    if encoding is None:
        logger.warning(f"Could not detect encoding for {file_path}, using utf-8")
        encoding = 'utf-8'

    metadata.update({
        'encoding': encoding,
        'delimiter': delimiter
    })

    return rows, metadata


def _open_file(path: Path, encoding: str = 'utf-8'):
    if path.name.endswith('.gz'):
        return gzip.open(path, 'rt', encoding=encoding, errors='ignore')
    return open(path, 'r', encoding=encoding, errors='ignore')
