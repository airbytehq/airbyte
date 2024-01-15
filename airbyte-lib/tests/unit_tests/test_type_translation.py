# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from sqlalchemy import types
from airbyte_lib.types import SQLTypeConverter

@pytest.mark.parametrize(
    "json_schema_property_def, expected_sql_type",
    [
        ({"type": "string"}, types.VARCHAR),
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
