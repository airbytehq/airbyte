#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union, Dict, List
import dateutil.parser

from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever


def is_valid_date_or_datetime_or_time(string: str) -> bool:
    try:
        dateutil.parser.parse(string)
        return True
    except ValueError:
        return False


def is_datetime(string: str) -> bool:
    try:
        dt = dateutil.parser.parse(string)
        dt.time()
        dt.date()
        return True
    except ValueError:
        return False


def is_time(string: str) -> bool:
    try:
        dt = dateutil.parser.parse(string)
        dt.time()
        return True
    except ValueError:
        return False


def is_date(string: str) -> bool:
    try:
        dt = dateutil.parser.parse(string)
        dt.date()
        return True
    except ValueError:
        return False


def map_value_to_schema_dtype(value: Any) -> Dict[str, Union[Dict[str, Any], str, List]]:
    if isinstance(value, bool):
        return {"type": ["boolean", "null"]}
    elif isinstance(value, int) or isinstance(value, float):
        return {"type": ["number", "null"]}
    elif isinstance(value, list):
        return {"type": ["array", "null"]}
    elif isinstance(value, str) and is_valid_date_or_datetime_or_time(value):
        if is_datetime(value):
            return {"type": ["string", "null"], "format": "date-time"}
        if is_date(value):
            return {"type": ["string", "null"], "format": "date"}
        if is_time(value):
            return {"type": ["string", "null"], "format": "time"}
        return {"type": ["string", "null"]}
    elif isinstance(value, str):
        return {"type": ["string", "null"]}
    elif isinstance(value, dict):
        nested_schema = {"properties": {}, "type": ["object", "null"]}
        for k, v in value.items():
            nested_schema["properties"][k] = map_value_to_schema_dtype(v)
        return nested_schema


def convert_record_to_schema(record: Dict[str, Any]) -> Dict[str, Any]:
    generated_schema = {
        "$schema": "http://json-schema.org/schema#",
        "additionalProperties": True,
        "properties": {},
        "type": "object"
    }
    for key, value in record.items():
        generated_schema["properties"][key] = map_value_to_schema_dtype(value)
    return generated_schema


@dataclass
class FirstRecordSchemaLoader(SchemaLoader):
    """Uses the first record to build a schema dynamically"""

    retriever: Retriever
    parameters: InitVar[Mapping[str, Any]]

    def get_json_schema(self) -> Mapping[str, Any]:
        first_record = next(self.retriever.read_records(record_schema={}))
        generated_schema = convert_record_to_schema(first_record)
        return generated_schema
