import csv
import gzip
import logging
from pathlib import Path
from typing import List

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

    logger.info(f"Found {len(csv_files)} CSV files")
    return csv_files

def open_csv_file(path: Path, encoding: str = 'utf-8'):
    if path.name.endswith('.gz'):
        return gzip.open(path, 'rt', encoding=encoding, errors='ignore')
    return open(path, 'r', encoding=encoding, errors='ignore')

def read_csv_file(file_path: Path, sample_size: int, delimiter_detection_sample_size: int) -> List[List[str]]:
    rows = []
    encoding = None
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    sniffer = csv.Sniffer()

    for enc in encodings_to_try:
        try:
            with open_csv_file(file_path, encoding=enc) as f:
                all_lines = [line for line in (f.readline() for _ in range(sample_size)) if line]
                if all_lines:
                    sample_text = ''.join(all_lines[:delimiter_detection_sample_size])
                    delimiter = sniffer.sniff(sample_text).delimiter
                    rows = list(csv.reader(all_lines, delimiter=delimiter))
                    encoding = enc
                    break

        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error sampling {file_path} with encoding {enc}: {e}")
            continue

    if encoding is None:
        logger.warning(f"Could not detect encoding for {file_path}, using utf-8")

    return rows
