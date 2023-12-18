#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.interpolation.macros import macros


@pytest.mark.parametrize(
    "test_name, fn_name, found_in_macros",
    [
        ("test_now_utc", "now_utc", True),
        ("test_today_utc", "today_utc", True),
        ("test_max", "max", True),
        ("test_day_delta", "day_delta", True),
        ("test_format_datetime", "format_datetime", True),
        ("test_duration", "duration", True),
        ("test_not_a_macro", "thisisnotavalidmacro", False),
    ],
)
def test_macros_export(test_name, fn_name, found_in_macros):
    if found_in_macros:
        assert fn_name in macros
    else:
        assert fn_name not in macros


@pytest.mark.parametrize(
    "test_name, input_value, format, expected_output",
    [
        ("test_datetime_string_to_date", "2022-01-01T01:01:01Z", "%Y-%m-%d", "2022-01-01"),
        ("test_date_string_to_date", "2022-01-01", "%Y-%m-%d", "2022-01-01"),
        ("test_datetime_string_to_date", "2022-01-01T00:00:00Z", "%Y-%m-%d", "2022-01-01"),
        ("test_datetime_with_tz_string_to_date", "2022-01-01T00:00:00Z", "%Y-%m-%d", "2022-01-01"),
        ("test_datetime_string_to_datetime", "2022-01-01T01:01:01Z", "%Y-%m-%dT%H:%M:%SZ", "2022-01-01T01:01:01Z"),
        ("test_datetime_string_with_tz_to_datetime", "2022-01-01T01:01:01-0800", "%Y-%m-%dT%H:%M:%SZ", "2022-01-01T09:01:01Z"),
        ("test_datetime_object_tz_to_date", datetime.datetime(2022, 1, 1, 1, 1, 1), "%Y-%m-%d", "2022-01-01"),
        ("test_datetime_object_tz_to_datetime", datetime.datetime(2022, 1, 1, 1, 1, 1), "%Y-%m-%dT%H:%M:%SZ", "2022-01-01T01:01:01Z"),
    ],
)
def test_format_datetime(test_name, input_value, format, expected_output):
    format_datetime = macros["format_datetime"]
    assert format_datetime(input_value, format) == expected_output


@pytest.mark.parametrize(
    "test_name, input_value, expected_output",
    [("test_one_day", "P1D", datetime.timedelta(days=1)), ("test_6_days_23_hours", "P6DT23H", datetime.timedelta(days=6, hours=23))],
)
def test_duration(test_name, input_value, expected_output):
    duration_fn = macros["duration"]
    assert duration_fn(input_value) == expected_output


@pytest.mark.parametrize(
    "test_name, input_value, expected_output",
    [
        ("test_int_input", 1646006400, 1646006400),
        ("test_float_input", 100.0, 100),
        ("test_float_input_is_floored", 100.9, 100),
        ("test_string_date_iso8601", "2022-02-28", 1646006400),
        ("test_string_datetime_midnight_iso8601", "2022-02-28T00:00:00Z", 1646006400),
        ("test_string_datetime_midnight_iso8601_with_tz", "2022-02-28T00:00:00-08:00", 1646035200),
        ("test_string_datetime_midnight_iso8601_no_t", "2022-02-28 00:00:00Z", 1646006400),
        ("test_string_datetime_iso8601", "2022-02-28T10:11:12", 1646043072),
    ],
)
def test_timestamp(test_name, input_value, expected_output):
    timestamp_function = macros["timestamp"]
    actual_output = timestamp_function(input_value)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "test_name, input_value, input_format, expected_output",
    [
        ("test_datetime_string_without_tz", "2024-01-01T01:01:01Z", "%Y-%m-%dT%H:%M:%SZ", datetime.datetime(2024, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)),
        ("test_datetime_string_with_tz", "2024-01-01T01:01:01-0800", "%Y-%m-%dT%H:%M:%S%z", datetime.datetime(2024, 1, 1, 9, 1, 1, tzinfo=datetime.timezone.utc)),
        ("test_datetime_string_with_tz", "2024-01-02T01:01:01+1100", "%Y-%m-%dT%H:%M:%S%z", datetime.datetime(2024, 1, 1, 14, 1, 1, tzinfo=datetime.timezone.utc)),
        ("test_date_string_without_tz", "2024-01-01Z", "%Y-%m-%dZ", datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)),
        ("test_date_string_with_tz", "2024-01-01+0400", "%Y-%m-%d%z", datetime.datetime(2023, 12, 31, 20, 0, 0, tzinfo=datetime.timezone.utc)),
    ],
)
def test_parse_datetime(test_name, input_value, input_format, expected_output):
    timestamp_function = macros["parse_datetime"]
    actual_output = timestamp_function(input_value, input_format)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "dt1, dt2, expected_delta",
    [
        pytest.param(
            datetime.datetime(2023, 12, 18, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
            datetime.timedelta(days=14),
            id="test_two_object_with_same_tz_d1_less_than_d2",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 4, tzinfo=datetime.timezone.utc),
            datetime.datetime(2023, 12, 15, tzinfo=datetime.timezone.utc),
            datetime.timedelta(days=20),
            id="test_two_object_with_same_tz_d2_less_than_d1",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 4, 2, tzinfo=datetime.timezone.utc),
            datetime.datetime.strptime("2024-01-01T01-0800", "%Y-%m-%dT%H%z"),
            datetime.timedelta(days=2, seconds=61200),
            id="test_two_datetime_object_with_diff_tz",
        ),
    ],
)
def test_compute_delta(dt1, dt2, expected_delta):
    timestamp_function = macros["compute_delta"]
    actual_output = timestamp_function(dt1, dt2)
    assert actual_output == expected_delta
