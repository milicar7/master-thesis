from typing import Dict, List, Set, Tuple

from csv_to_ddl.config.default_config import KeyConfig
from csv_to_ddl.models.table import TableSpec


def get_table_headers(table_name: str, table_specs: Dict[str, TableSpec]) -> List[str]:
    table_spec = table_specs.get(table_name)
    if table_spec:
        return [col.name for col in table_spec.columns]
    return []


def get_single_column_values_from_data(column_name: str,
                                       table_data: List[List[str]],
                                       table_headers: List[str]) -> Set[str]:
    if not table_data or not table_headers:
        return set()

    try:
        col_index = table_headers.index(column_name)
    except ValueError:
        return set()

    values = set()
    for row in table_data:
        if col_index < len(row) and row[col_index] is not None:
            value = str(row[col_index]).strip()
            if value:
                values.add(value)

    return values


def get_composite_values_from_data(table_name: str, column_names: List[str],
                                   tables_data: Dict[str, List[List[str]]],
                                   table_headers: List[str]) -> Set[Tuple[str, ...]]:
    table_data = tables_data.get(table_name, [])
    if not table_data or not table_headers:
        return set()

    try:
        col_indices = [table_headers.index(col_name) for col_name in column_names]
    except ValueError:
        return set()

    values = set()
    for row in table_data:
        if all(idx < len(row) for idx in col_indices):
            combo = tuple(str(row[idx]).strip() for idx in col_indices)
            if all(val for val in combo):
                values.add(combo)

    return values


def build_reference_keys_map(table_specs: Dict[str, TableSpec],
                             tables_data: Dict[str, List[List[str]]],
                             config: KeyConfig) -> Dict[str, Dict]:
    reference_keys = {}

    for table_name, table_spec in table_specs.items():
        reference_keys[table_name] = {
            'single_keys': {},
            'composite_keys': {},
            'headers': get_table_headers(table_name, table_specs),
            'primary_key_columns': set()
        }

        table_headers = reference_keys[table_name]['headers']
        table_data = tables_data.get(table_name, [])
        if not table_headers:
            continue

        pk_columns = table_spec.primary_key.columns if table_spec.primary_key else None
        if pk_columns:
            reference_keys[table_name]['primary_key_columns'].update(pk_columns)

            if len(pk_columns) == 1:
                pk_values = get_single_column_values_from_data(pk_columns[0], table_data, table_headers)
                if pk_values:
                    reference_keys[table_name]['single_keys'][pk_columns[0]] = pk_values
            else:
                pk_values = get_composite_values_from_data(table_name, pk_columns, tables_data, table_headers)
                if pk_values:
                    reference_keys[table_name]['composite_keys'][tuple(pk_columns)] = pk_values

        for col in table_spec.columns:
            if (col.statistics
                    and col.statistics.unique_ratio >= config.pk_single_uniqueness_threshold
                    and col.statistics.distinct_count > 1
                    and col.name not in reference_keys[table_name]['single_keys']):
                col_values = get_single_column_values_from_data(col.name, table_data, table_headers)
                if col_values:
                    reference_keys[table_name]['single_keys'][col.name] = col_values

    return reference_keys
