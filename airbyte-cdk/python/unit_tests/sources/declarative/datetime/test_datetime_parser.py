#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser


@pytest.mark.parametrize(
    "test_name, input_date, date_format, expected_output_date",
    [
        (
            "test_parse_date_iso",
            "2021-01-01T00:00:00.000000+0000",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_parse_date_iso_with_timezone_not_utc",
            "2021-01-01T00:00:00.000000+0400",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=14400))),
        ),
        (
            "test_parse_timestamp",
            "1609459200",
            "%s",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_parse_timestamp_as_float",
            "1675092508.873709",
            "%s_as_float",
            datetime.datetime(2023, 1, 30, 15, 28, 28, 873709, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_parse_ms_timestamp",
            "1609459200001",
            "%ms",
            datetime.datetime(2021, 1, 1, 0, 0, 0, 1000, tzinfo=datetime.timezone.utc),
        ),
        ("test_parse_date_ms", "20210101", "%Y%m%d", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    ],
)
def test_parse_date(test_name, input_date, date_format, expected_output_date):
    parser = DatetimeParser()
    output_date = parser.parse(input_date, date_format)
    assert output_date == expected_output_date


@pytest.mark.parametrize(
    "test_name, input_dt, datetimeformat, expected_output",
    [
        ("test_format_timestamp", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%s", "1609459200"),
        ("test_format_timestamp_ms", datetime.datetime(2021, 1, 1, 0, 0, 0, 1000, tzinfo=datetime.timezone.utc), "%ms", "1609459200001"),
        ("test_format_timestamp_as_float", datetime.datetime(2023, 1, 30, 15, 28, 28, 873709, tzinfo=datetime.timezone.utc), "%s_as_float", "1675092508.873709"),
        ("test_format_string", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y-%m-%d", "2021-01-01"),
        ("test_format_to_number", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y%m%d", "20210101"),
    ],
)
def test_format_datetime(test_name, input_dt, datetimeformat, expected_output):
    parser = DatetimeParser()
    output_date = parser.format(input_dt, datetimeformat)
    assert output_date == expected_output
