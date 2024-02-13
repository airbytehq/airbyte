# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from sqlalchemy import types
from airbyte_lib.types import SQLTypeConverter, _get_airbyte_type


@pytest.mark.parametrize(
    "json_schema_property_def, expected_sql_type",
    [
        ({"type": "string"}, types.VARCHAR),
        ({"type": ["boolean", "null"]}, types.BOOLEAN),
        ({"type": ["null", "boolean"]}, types.BOOLEAN),
        ({"type": "string"}, types.VARCHAR),
        ({"type": ["null", "string"]}, types.VARCHAR),
        ({"type": "boolean"}, types.BOOLEAN),
        ({"type": "string", "format": "date"}, types.DATE),
        ({"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"}, types.TIMESTAMP),
        ({"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}, types.TIMESTAMP),
        ({"type": "string", "format": "time", "airbyte_type": "time_without_timezone"}, types.TIME),
        ({"type": "string", "format": "time", "airbyte_type": "time_with_timezone"}, types.TIME),
        ({"type": "integer"}, types.BIGINT),
        ({"type": "number", "airbyte_type": "integer"}, types.BIGINT),
        ({"type": "number"}, types.DECIMAL),
        ({"type": "array"}, types.VARCHAR),
        ({"type": "object"}, types.VARCHAR),
    ],
)
def test_to_sql_type(json_schema_property_def, expected_sql_type):
    converter = SQLTypeConverter()
    sql_type = converter.to_sql_type(json_schema_property_def)
    assert isinstance(sql_type, expected_sql_type)


@pytest.mark.parametrize(
    "json_schema_property_def, expected_airbyte_type",
    [
        ({"type": "string"}, "string"),
        ({"type": ["boolean", "null"]}, "boolean"),
        ({"type": ["null", "boolean"]}, "boolean"),
        ({"type": "string"}, "string"),
        ({"type": ["null", "string"]}, "string"),
        ({"type": "boolean"}, "boolean"),
        ({"type": "string", "format": "date"}, "date"),
        ({"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"}, "timestamp_without_timezone"),
        ({"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}, "timestamp_with_timezone"),
        ({"type": "string", "format": "time", "airbyte_type": "time_without_timezone"}, "time_without_timezone"),
        ({"type": "string", "format": "time", "airbyte_type": "time_with_timezone"}, "time_with_timezone"),
        ({"type": "integer"}, "integer"),
        ({"type": "number", "airbyte_type": "integer"}, "integer"),
        ({"type": "number"}, "number"),
        ({"type": "array"}, "array"),
        ({"type": "object"}, "object"),
    ],
)
def test_to_airbyte_type(json_schema_property_def, expected_airbyte_type):
    airbyte_type, _ = _get_airbyte_type(json_schema_property_def)
    assert airbyte_type == expected_airbyte_type


@pytest.mark.parametrize(
    "json_schema_property_def, expected_airbyte_type, expected_airbyte_subtype",
    [
        ({"type": "string"}, "string", None),
        ({"type": "number"}, "number", None),
        ({"type": "array"}, "array", None),
        ({"type": "object"}, "object", None),
        ({"type": "array", "items": {"type": ["null", "string"]}}, "array", "string"),
        ({"type": "array", "items": {"type": ["boolean"]}}, "array", "boolean"),
    ],
)
def test_to_airbyte_subtype(
    json_schema_property_def,
    expected_airbyte_type,
    expected_airbyte_subtype,
):
    airbyte_type, subtype = _get_airbyte_type(json_schema_property_def)
    assert airbyte_type == expected_airbyte_type
    assert subtype == expected_airbyte_subtype
