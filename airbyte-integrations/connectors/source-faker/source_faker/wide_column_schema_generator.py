#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
https://docs.airbyte.com/understanding-airbyte/supported-data-types/
- String	{"type": "string"}	"foo bar"
- Boolean	{"type": "boolean"}	true or false
- Date	{"type": "string", "format": "date"}	"2021-01-23", "2021-01-23 BC"
- Timestamp without timezone	{"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"}	"2022-11-22T01:23:45", "2022-11-22T01:23:45.123456 BC"
- Timestamp with timezone	{"type": "string", "format": "date-time"}; optionally "airbyte_type": "timestamp_with_timezone"	"2022-11-22T01:23:45.123456+05:00", "2022-11-22T01:23:45Z BC"
- Time without timezone	{"type": "string", "format": "time", "airbyte_type": "time_without_timezone"}	"01:23:45.123456", "01:23:45"
- Time with timezone	{"type": "string", "format": "time", "airbyte_type": "time_with_timezone"}	"01:23:45.123456+05:00", "01:23:45Z"
- Integer	{"type": "integer"} or {"type": "number", "airbyte_type": "integer"}	42
- Number	{"type": "number"}	1234.56
- Array	{"type": "array"}; optionally items	[1, 2, 3]
- Object	{"type": "object"}; optionally properties	{"foo": "bar"}
- Union	{"oneOf": [...]}	
"""

from typing import Any, List, Mapping, Tuple, Union


def simple_property(name: str, type: Union[str, List[str]]) -> Tuple[str, Mapping[str, Any]]:
    return name, {"type": type}


def date_property(name: str, format: str, airbyte_type: str) -> Tuple[str, Mapping[str, Any]]:
    definition = {
        "type": ["null", "string"],
        "format": format,
    }
    if airbyte_type is not None:
        definition["airbyte_type"] = airbyte_type
    return name, definition


def union_property(name: str) -> Tuple[str, Mapping[str, Any]]:
    # Keeping this simple for now
    return name, {"oneOf": ["string", "number"]}


all_supported_column_type_property_generators = [
    lambda i: simple_property(f"string_{i}", "string"),
    lambda i: simple_property(f"boolean_{i}", "boolean"),
    lambda i: date_property(f"date_{i}", "date", None),
    lambda i: date_property(f"timestamp_wo_tz_{i}", "date-time", "timestamp_without_timezone"),
    lambda i: date_property(f"timestamp_w_tz_{i}", "date-time", "timestamp_with_timezone"),
    lambda i: date_property(f"time_wo_tz_{i}", "time", "time_without_timezone"),
    lambda i: date_property(f"time_w_tz_{i}", "time", "time_with_timezone"),
    lambda i: simple_property(f"integer_{i}", "integer"),
    lambda i: simple_property(f"number_{i}", "number"),
    lambda i: simple_property(f"array_{i}", "array"),
    lambda i: simple_property(f"object_{i}", "object"),
    lambda i: union_property(f"union_{i}"),
]


def generate_wide_schema(columns: int) -> Mapping[str, Any]:
    """Generate a schema for the WideColumn stream. Uses a round robin approach to the supported Airbyte types
    defined in all_supported_column_type_property_generators above

    Args:
        columns (int): How many columns should be in this schema

    Returns:
        Mapping[str, Any]: A Schema compatible with Airbyte's Streams
    """
    full_schema = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object"}
    properties = dict()
    # special case id and updated_at column
    id = simple_property("id", "integer")
    properties[id[0]] = id[1]
    properties["updated_at"] = {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
    column_count = 2
    property_generator_index = 0
    while column_count < columns:
        property_info = all_supported_column_type_property_generators[property_generator_index](column_count)
        properties[property_info[0]] = property_info[1]

        property_generator_index += 1
        if property_generator_index == len(all_supported_column_type_property_generators):
            property_generator_index = 0
        column_count += 1

    full_schema["properties"] = properties

    return full_schema, list(properties.keys())
