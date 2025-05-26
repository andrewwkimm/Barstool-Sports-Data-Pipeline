"""The JSONL File Reader."""

import json
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Union

import pyarrow as pa


def read_jsonl_file(jsonl_file: Union[BinaryIO, Path]) -> pa.table:
    """Reads a JSONL file and converts it to a PyArrow table."""
    raw_data = load_jsonl_file(jsonl_file)
    flat_data = normalize_data(raw_data, nested_fields=["LOG", "GEO"])
    table = convert_to_table(flat_data)
    return table


def load_jsonl_file(source: Union[BinaryIO, Path]) -> List[Dict[str, Any]]:
    """Loads either the BinaryIO or Path form of the JSONL into memory."""
    if isinstance(source, Path):
        content = source.read_text()
    else:
        content = source.read().decode("utf-8")
    return json.loads(content)


def parse_nested_json_fields(
    record: Dict[str, Any], nested_fields: List[str]
) -> Dict[str, Any]:
    """Parses nested values into each individual column."""
    result = record.copy()

    for field in nested_fields:
        if field in record and isinstance(record[field], str):
            try:
                nested_data = json.loads(record[field])
                for k, v in nested_data.items():
                    if isinstance(v, dict):
                        for subk, subv in v.items():
                            result[f"{k}_{subk}"] = subv
                    else:
                        result[k] = v
                del result[field]
            except json.JSONDecodeError:
                pass
    return result


def normalize_data(
    data: List[Dict[str, Any]], nested_fields: List[str]
) -> List[Dict[str, Any]]:
    """Normalizes the data into tabular form."""
    normalized_data = [
        parse_nested_json_fields(record, nested_fields) for record in data
    ]
    return normalized_data


def convert_to_table(data: List[Dict[str, Any]]) -> pa.Table:
    """Converts data into a PyArrow table."""
    keys = {k for row in data for k in row}
    columns = {k: [row.get(k) for row in data] for k in keys}

    table = pa.table(columns)
    return table
