import json
import re
import statistics
from collections import Counter
from datetime import datetime
from typing import Dict, Any
from typing import List, Tuple


def is_boolean(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    boolean_values = {
        'true', 'false', '1', '0', 'yes', 'no', 'y', 'n',
        't', 'f', 'on', 'off', 'enabled', 'disabled'
    }

    matches = sum(1 for v in values if v.lower() in boolean_values)
    ratio = matches / len(values) if values else 0

    return ratio, {'boolean_patterns': list(set(v.lower() for v in values if v.lower() in boolean_values))}


def is_integer(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    matches = 0
    min_val, max_val = float('inf'), float('-inf')

    for v in values:
        if re.match(r'^-?\d+$', v):
            matches += 1
            val = int(v)
            min_val = min(min_val, val)
            max_val = max(max_val, val)

    ratio = matches / len(values) if values else 0
    metadata = {}

    if matches > 0:
        metadata['min_value'] = min_val
        metadata['max_value'] = max_val
        metadata['range'] = max_val - min_val

    return ratio, metadata


def is_bigint(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    matches = 0
    int_range = 2 ** 31

    for v in values:
        if re.match(r'^-?\d+$', v):
            try:
                val = int(v)
                if abs(val) > int_range:
                    matches += 1
            except ValueError:
                continue

    ratio = matches / len(values) if values else 0
    return ratio, {'threshold': int_range}


def is_decimal(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    decimal_pattern = re.compile(r'^-?\d+\.\d+$')
    matches = 0
    decimal_places = []

    for v in values:
        if decimal_pattern.match(v):
            matches += 1
            places = len(v.split('.')[1])
            decimal_places.append(places)

    ratio = matches / len(values) if values else 0
    metadata = {}

    if decimal_places:
        metadata['avg_decimal_places'] = statistics.mean(decimal_places)
        metadata['max_decimal_places'] = max(decimal_places)
        metadata['consistent_places'] = len(set(decimal_places)) == 1

    return ratio, metadata


def is_float(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    matches = 0

    for v in values:
        try:
            float(v)
            if '.' in v or 'e' in v.lower():
                matches += 1
        except ValueError:
            continue

    ratio = matches / len(values) if values else 0
    return ratio, {}


def is_uuid(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )

    matches = sum(1 for v in values if uuid_pattern.match(v))
    ratio = matches / len(values) if values else 0

    return ratio, {}


def is_email(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    matches = sum(1 for v in values if email_pattern.match(v))
    ratio = matches / len(values) if values else 0

    domains = []
    if matches > 0:
        for v in values:
            if email_pattern.match(v):
                domain = v.split('@')[1]
                domains.append(domain)

    return ratio, {'unique_domains': len(set(domains)), 'top_domains': Counter(domains).most_common(3)}


def is_url(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    url_pattern = re.compile(r'^https?://[^\s/$.?#].\S*$', re.IGNORECASE)

    matches = sum(1 for v in values if url_pattern.match(v))
    ratio = matches / len(values) if values else 0

    return ratio, {}


def is_date(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    date_formats: List[str] = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
                               "%d-%m-%Y", "%m-%d-%Y", "%Y.%m.%d", "%d.%m.%Y"]

    matches = 0
    successful_formats = []

    for v in values:
        for fmt in date_formats:
            try:
                datetime.strptime(v, fmt)
                matches += 1
                successful_formats.append(fmt)
                break
            except ValueError:
                continue

    ratio = matches / len(values) if values else 0
    metadata = {}

    if successful_formats:
        format_counts = Counter(successful_formats)
        metadata['detected_formats'] = format_counts.most_common(3)

    return ratio, metadata


def is_datetime(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    datetime_formats: List[str] = ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S",
                                   "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]
    matches = 0
    successful_formats = []

    for v in values:
        for fmt in datetime_formats:
            try:
                datetime.strptime(v, fmt)
                matches += 1
                successful_formats.append(fmt)
                break
            except ValueError:
                continue

    ratio = matches / len(values) if values else 0
    metadata = {}

    if successful_formats:
        format_counts = Counter(successful_formats)
        metadata['detected_formats'] = format_counts.most_common(3)

    return ratio, metadata


def is_time(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    time_patterns = [
        r'^\d{1,2}:\d{2}:\d{2}$',  # HH:MM:SS
        r'^\d{1,2}:\d{2}$',  # HH:MM
        r'^\d{1,2}:\d{2}:\d{2}\.\d+$',  # HH:MM:SS.fff
    ]

    matches = 0
    for v in values:
        for pattern in time_patterns:
            if re.match(pattern, v):
                matches += 1
                break

    ratio = matches / len(values) if values else 0
    return ratio, {}


def is_json(values: List[str]) -> Tuple[float, Dict[str, Any]]:
    matches = 0

    for v in values:
        v = v.strip()
        if (v.startswith('{') and v.endswith('}')) or (v.startswith('[') and v.endswith(']')):
            try:
                json.loads(v)
                matches += 1
            except json.JSONDecodeError:
                continue

    ratio = matches / len(values) if values else 0
    return ratio, {}