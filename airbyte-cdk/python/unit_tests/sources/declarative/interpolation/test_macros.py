#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.interpolation.macros import macros


@pytest.fixture
def frozen_datetime_now(monkeypatch):
    """Mock the datetime object's now() method to return a specific date"""
    datetime_mock = MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = datetime.datetime(2022, 1, 1, 1, 1, 1)
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


@pytest.mark.parametrize(
    "test_name, fn_name, found_in_macros",
    [
        ("test_now_local", "now_local", True),
        ("test_now_utc", "now_utc", True),
        ("test_today_utc", "today_utc", True),
        ("test_max", "max", True),
        ("test_day_delta", "day_delta", True),
        ("test_format_datetime", "format_datetime", True),
        ("test_as_timezone", "as_timezone", True),
        ("test_not_a_macro", "thisisnotavalidmacro", False),
    ],
)
def test_macros_export(test_name, fn_name, found_in_macros):
    if found_in_macros:
        assert fn_name in macros
    else:
        assert fn_name not in macros


def test_format_datetime():
    format_datetime = macros["format_datetime"]
    assert format_datetime("2022-01-01T01:01:01Z", "%Y-%m-%d") == "2022-01-01"
    assert format_datetime(datetime.datetime(2022, 1, 1, 1, 1, 1), "%Y-%m-%d") == "2022-01-01"


def test_day_delta_no_from_date(frozen_datetime_now):
    day_delta = macros["day_delta"]
    assert day_delta(1) == "2022-01-02T01:01:01.000000"
    assert day_delta(-1) == "2021-12-31T01:01:01.000000"
    assert day_delta(0) == "2022-01-01T01:01:01.000000"


def test_day_delta_with_from_date(frozen_datetime_now):
    day_delta = macros["day_delta"]
    assert day_delta(1, "2022-01-01T01:01:01") == "2022-01-02T01:01:01.000000"
    assert day_delta(1, "2022-01-01T01:01:01Z") == "2022-01-02T01:01:01.000000+0000"
    assert day_delta(1, datetime.datetime(2022, 1, 1, 1, 1, 1)) == "2022-01-02T01:01:01.000000"
    assert day_delta(1, datetime.datetime(2022, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)) == "2022-01-02T01:01:01.000000+0000"


def test_as_timezone():
    as_timezone = macros["as_timezone"]
    assert as_timezone("2022-01-01T01:01:01Z", "UTC") == datetime.datetime(2022, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)
    assert as_timezone("2022-01-01T01:01:01", "UTC") == datetime.datetime(2022, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)
    assert as_timezone("2022-01-01T01:01:01Z", "America/New_York") == (
        datetime.datetime(2021, 12, 31, 20, 1, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    )
    assert as_timezone("2022-01-01T01:01:01+0300", "America/New_York") == (
        datetime.datetime(2021, 12, 31, 17, 1, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    )
