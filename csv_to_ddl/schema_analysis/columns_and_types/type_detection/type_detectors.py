import json
import re
from datetime import datetime
from typing import List


def is_boolean(values: List[str]) -> float:
    """
    Detect boolean data type by pattern matching common boolean representations.
    
    Recognizes various boolean formats including:
    - Standard: true/false, 1/0
    - Common variations: yes/no, y/n, t/f
    - System states: on/off, enabled/disabled
    
    Returns:
        Confidence ratio (0.0-1.0) based on how many values match boolean patterns
    """
    boolean_values = {
        'true', 'false', '1', '0', 'yes', 'no', 'y', 'n',
        't', 'f', 'on', 'off', 'enabled', 'disabled'
    }

    matches = sum(1 for v in values if v.lower() in boolean_values)
    return matches / len(values) if values else 0


def is_integer(values: List[str]) -> float:
    """
    Detect integer data type using regex pattern matching.
    
    Matches whole numbers (positive and negative) without decimal points.
    Also tracks min/max values for potential size optimization.
    Pattern: '^-?\\d+$' matches optional minus sign followed by one or more digits.
    
    Returns:
        Confidence ratio based on how many values match integer pattern
    """
    matches = 0
    min_val, max_val = float('inf'), float('-inf')

    for v in values:
        if re.match(r'^-?\d+$', v):
            matches += 1
            val = int(v)
            min_val = min(min_val, val)
            max_val = max(max_val, val)

    return matches / len(values) if values else 0


def is_bigint(values: List[str]) -> float:
    """
    Detect if integers require BIGINT data type due to size constraints.
    
    Checks if integer values exceed standard 32-bit integer range (2^31).
    This helps determine when to use BIGINT instead of regular INTEGER type.
    Only counts values that exceed the standard integer range.
    
    Returns:
        Ratio of values that require BIGINT storage
    """
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

    return matches / len(values) if values else 0


def is_decimal(values: List[str]) -> float:
    decimal_pattern = re.compile(r'^-?\d+\.\d+$')
    matches = 0
    decimal_places = []

    for v in values:
        if decimal_pattern.match(v):
            matches += 1
            places = len(v.split('.')[1])
            decimal_places.append(places)

    return matches / len(values) if values else 0


def is_float(values: List[str]) -> float:
    matches = 0

    for v in values:
        try:
            float(v)
            if '.' in v or 'e' in v.lower():
                matches += 1
        except ValueError:
            continue

    return matches / len(values) if values else 0


def is_uuid(values: List[str]) -> float:
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )

    matches = sum(1 for v in values if uuid_pattern.match(v))
    return matches / len(values) if values else 0


def is_email(values: List[str]) -> float:
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    matches = sum(1 for v in values if email_pattern.match(v))
    return matches / len(values) if values else 0


def is_url(values: List[str]) -> float:
    url_pattern = re.compile(r'^https?://[^\s/$.?#].\S*$', re.IGNORECASE)

    matches = sum(1 for v in values if url_pattern.match(v))
    return matches / len(values) if values else 0


def is_date(values: List[str]) -> float:
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

    return matches / len(values) if values else 0


def is_datetime(values: List[str]) -> float:
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

    return matches / len(values) if values else 0


def is_time(values: List[str]) -> float:
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

    return matches / len(values) if values else 0


def is_json(values: List[str]) -> float:
    matches = 0

    for v in values:
        v = v.strip()
        if (v.startswith('{') and v.endswith('}')) or (v.startswith('[') and v.endswith(']')):
            try:
                json.loads(v)
                matches += 1
            except json.JSONDecodeError:
                continue

    return matches / len(values) if values else 0
