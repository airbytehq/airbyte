#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
            "test_parse_timestamp",
            "1609459200",
            "%s",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        ("test_parse_date_number", "20210101", "%Y%m%d", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    ],
)
def test_parse_date(test_name, input_date, date_format, expected_output_date):
    parser = DatetimeParser()
    output_date = parser.parse(input_date, date_format, datetime.timezone.utc)
    assert expected_output_date == output_date


@pytest.mark.parametrize(
    "test_name, input_dt, datetimeformat, expected_output",
    [
        ("test_format_timestamp", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%s", "1609459200"),
        ("test_format_string", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y-%m-%d", "2021-01-01"),
        ("test_format_to_number", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y%m%d", "20210101"),
    ],
)
def test_format_datetime(test_name, input_dt, datetimeformat, expected_output):
    parser = DatetimeParser()
    output_date = parser.format(input_dt, datetimeformat)
    assert expected_output == output_date
