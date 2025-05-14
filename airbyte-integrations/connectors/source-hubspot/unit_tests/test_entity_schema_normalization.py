#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from source_hubspot.components import EntitySchemaNormalization


@pytest.mark.parametrize(
    "original_value,field_schema,expected_value",
    [
        pytest.param("sample_string", {"type": ["null", "string"]}, "sample_string", id="test_string_transform"),
        pytest.param("", {"type": ["null", "number"]}, None, id="test_empty_string_returns_none"),
        pytest.param("700.0", {"type": ["null", "number"]}, 700.0, id="test_transform_float"),
        pytest.param("10293848576", {"type": ["null", "number"]}, 10293848576, id="test_do_not_cast_numeric_id_to_float"),
        pytest.param("true", {"type": ["null", "boolean"]}, True, id="test_transform_boolean_true"),
        pytest.param("false", {"type": ["null", "boolean"]}, False, id="test_transform_boolean_false"),
        pytest.param("Not real", {"type": ["null", "boolean"]}, "Not real", id="test_do_not_transform_non_boolean"),
        pytest.param("TrUe", {"type": ["null", "boolean"]}, True, id="test_transform_boolean_case_insensitive"),
        pytest.param(
            "2025-02-19T11:49:03.544Z",
            {"type": "string", "format": "date-time"},
            "2025-02-19T11:49:03.544000+00:00",
            id="test_transform_datetime_string",
        ),
        pytest.param("1746082800", {"type": "string", "format": "date"}, "2025-05-01", id="test_timestamp_seconds_to_date"),
        pytest.param(
            "1746082800", {"type": "string", "format": "date-time"}, "2025-05-01T07:00:00+00:00", id="test_timestamp_seconds_to_datetime"
        ),
        pytest.param(
            "1746082800",
            {"type": "string", "format": "date-time", "__ab_apply_cast_datetime": False},
            "1746082800",
            id="test_do_not_apply_cast_datetime",
        ),
        pytest.param("not_parsable_date", {"type": "string", "format": "date"}, "not_parsable_date", id="test_do_not_apply_cast_datetime"),
    ],
)
def test_entity_schema_normalization(original_value, field_schema, expected_value):
    transform_function = EntitySchemaNormalization().get_transform_function()

    transformed_value = transform_function(original_value=original_value, field_schema=field_schema)
    assert type(transformed_value) == type(expected_value)
    assert transformed_value == expected_value
