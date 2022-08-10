#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_hubspot.streams import Stream


@pytest.mark.parametrize(
    "field_type,expected",
    [
        ("string", {"type": ["null", "string"]}),
        ("integer", {"type": ["null", "integer"]}),
        ("number", {"type": ["null", "number"]}),
        ("bool", {"type": ["null", "boolean"]}),
        ("boolean", {"type": ["null", "boolean"]}),
        ("enumeration", {"type": ["null", "string"]}),
        ("object", {"type": ["null", "object"]}),
        ("array", {"type": ["null", "array"]}),
        ("date", {"type": ["null", "string"], "format": "date"}),
        ("date-time", {"type": ["null", "string"], "format": "date-time"}),
        ("datetime", {"type": ["null", "string"], "format": "date-time"}),
        ("json", {"type": ["null", "string"]}),
        ("phone_number", {"type": ["null", "string"]}),
    ],
)
def test_field_type_format_converting(field_type, expected):
    assert Stream._get_field_props(field_type=field_type) == expected


@pytest.mark.parametrize(
    "field_type,expected",
    [
        ("_unsupported_field_type_", {"type": ["null", "string"]}),
        (None, {"type": ["null", "string"]}),
        (1, {"type": ["null", "string"]}),
    ],
)
def test_bad_field_type_converting(field_type, expected, caplog, capsys):

    assert Stream._get_field_props(field_type=field_type) == expected

    logs = caplog.records

    assert logs
    assert logs[0].levelname == "WARNING"
    assert logs[0].msg == f"Unsupported type {field_type} found"


@pytest.mark.parametrize(
    "declared_field_types,field_name,field_value,format,casted_value",
    [
        # test for None in field_values
        (["null", "string"], "some_field", None, None, None),
        (["null", "number"], "some_field", None, None, None),
        (["null", "integer"], "some_field", None, None, None),
        (["null", "object"], "some_field", None, None, None),
        (["null", "boolean"], "some_field", None, None, None),
        # specific cases
        ("string", "some_field", "test", None, "test"),
        (["null", "number"], "some_field", "123.456", None, 123.456),
        (["null", "number"], "some_field", "123,123.456", None, 123123.456),
        (["null", "number"], "user_id", "123", None, 123),
        (["null", "string"], "some_field", "123", None, "123"),
        # when string has empty field_value (empty string)
        (["null", "string"], "some_field", "", None, ""),
        # when NOT string type but has empty sting in field_value, instead of double or null,
        # we should use None instead, to have it properly casted to the correct type
        (["null", "number"], "some_field", "", None, None),
        (["null", "integer"], "some_field", "", None, None),
        (["null", "object"], "some_field", "", None, None),
        (["null", "boolean"], "some_field", "", None, None),
        # Test casting fields with format specified
        (["null", "string"], "some_field", "", "date-time", None),
        (["string"], "some_field", "", "date-time", ""),
        (["null", "string"], "some_field", "2020", "date-time", "2020-01-01T00:00:00+00:00"),
    ],
)
def test_cast_type_if_needed(declared_field_types, field_name, field_value, format, casted_value):
    assert (
        Stream._cast_value(
            declared_field_types=declared_field_types, field_name=field_name, field_value=field_value, declared_format=format
        )
        == casted_value
    )


@pytest.mark.parametrize(
    "field_value, declared_format, expected_casted_value",
    [
        ("1653696000000", "date", "2022-05-28"),
        ("1645608465000", "date-time", "2022-02-23T09:27:45+00:00"),
        (1645608465000, "date-time", "2022-02-23T09:27:45+00:00"),
        ("2022-05-28", "date", "2022-05-28"),
        ("2022-02-23 09:27:45", "date-time", "2022-02-23T09:27:45+00:00"),
        ("", "date", ""),
        (None, "date", None),
        ("2022-02-23 09:27:45", "date", "2022-02-23"),
        ("2022-05-28", "date-time", "2022-05-28T00:00:00+00:00"),
    ],
)
def test_cast_timestamp_to_date(field_value, declared_format, expected_casted_value):
    casted_value = Stream._cast_datetime("hs_recurring_billing_end_date", field_value, declared_format=declared_format)
    assert casted_value == expected_casted_value
