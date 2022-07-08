#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import unittest

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer

datetime_format = "%Y-%m-%d"
FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01"}
end_date_now = InterpolatedString(
    "{{ today_utc() }}",
)
cursor_value = InterpolatedString("{{ stream_state['date'] }}")
timezone = datetime.timezone.utc


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    datetime_mock = unittest.mock.MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_NOW
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


@pytest.mark.parametrize(
    "test_name, stream_state, start, end, step, cursor, expected_slices",
    [
        (
            "test_1_day",
            None,
            MinMaxDatetime("{{ config['start_date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            "1d",
            cursor_value,
            [
                {"start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"start_date": "2021-01-03", "end_date": "2021-01-03"},
                {"start_date": "2021-01-04", "end_date": "2021-01-04"},
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
                {"start_date": "2021-01-06", "end_date": "2021-01-06"},
                {"start_date": "2021-01-07", "end_date": "2021-01-07"},
                {"start_date": "2021-01-08", "end_date": "2021-01-08"},
                {"start_date": "2021-01-09", "end_date": "2021-01-09"},
                {"start_date": "2021-01-10", "end_date": "2021-01-10"},
            ],
        ),
        (
            "test_2_day",
            None,
            MinMaxDatetime("{{ config['start_date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            "2d",
            cursor_value,
            [
                {"start_date": "2021-01-01", "end_date": "2021-01-02"},
                {"start_date": "2021-01-03", "end_date": "2021-01-04"},
                {"start_date": "2021-01-05", "end_date": "2021-01-06"},
                {"start_date": "2021-01-07", "end_date": "2021-01-08"},
                {"start_date": "2021-01-09", "end_date": "2021-01-10"},
            ],
        ),
        (
            "test_from_stream_state",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ stream_state['date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            "1d",
            cursor_value,
            [
                # FIXME: should this include 2021-01-05?
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
                {"start_date": "2021-01-06", "end_date": "2021-01-06"},
                {"start_date": "2021-01-07", "end_date": "2021-01-07"},
                {"start_date": "2021-01-08", "end_date": "2021-01-08"},
                {"start_date": "2021-01-09", "end_date": "2021-01-09"},
                {"start_date": "2021-01-10", "end_date": "2021-01-10"},
            ],
        ),
        (
            "test_12_day",
            None,
            MinMaxDatetime("{{ config['start_date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            "12d",
            cursor_value,
            [
                {"start_date": "2021-01-01", "end_date": "2021-01-10"},
            ],
        ),
        (
            "test_end_date_greater_than_now",
            None,
            MinMaxDatetime("2021-12-28", datetime_format=datetime_format),
            MinMaxDatetime(f"{(FAKE_NOW + datetime.timedelta(days=1)).strftime(datetime_format)}", datetime_format=datetime_format),
            "1d",
            cursor_value,
            [
                {"start_date": "2021-12-28", "end_date": "2021-12-28"},
                {"start_date": "2021-12-29", "end_date": "2021-12-29"},
                {"start_date": "2021-12-30", "end_date": "2021-12-30"},
                {"start_date": "2021-12-31", "end_date": "2021-12-31"},
                {"start_date": "2022-01-01", "end_date": "2022-01-01"},
            ],
        ),
        (
            "test_start_date_greater_than_end_date",
            {"date": "2021-01-05"},
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            MinMaxDatetime("{{ stream_state['date'] }}", datetime_format=datetime_format),
            "1d",
            cursor_value,
            [
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ stream_state['date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            "1d",
            InterpolatedString("{{ stream_state['date'] }}"),
            [
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
                {"start_date": "2021-01-06", "end_date": "2021-01-06"},
                {"start_date": "2021-01-07", "end_date": "2021-01-07"},
                {"start_date": "2021-01-08", "end_date": "2021-01-08"},
                {"start_date": "2021-01-09", "end_date": "2021-01-09"},
                {"start_date": "2021-01-10", "end_date": "2021-01-10"},
            ],
        ),
        (
            "test_start_date_less_than_min_date",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ config['start_date'] }}", min_datetime="{{ stream_state['date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", datetime_format=datetime_format),
            "1d",
            InterpolatedString("{{ stream_state['date'] }}"),
            [
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
                {"start_date": "2021-01-06", "end_date": "2021-01-06"},
                {"start_date": "2021-01-07", "end_date": "2021-01-07"},
                {"start_date": "2021-01-08", "end_date": "2021-01-08"},
                {"start_date": "2021-01-09", "end_date": "2021-01-09"},
                {"start_date": "2021-01-10", "end_date": "2021-01-10"},
            ],
        ),
        (
            "test_end_date_greater_than_max_date",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ config['start_date'] }}", datetime_format=datetime_format),
            MinMaxDatetime("2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format=datetime_format),
            "1d",
            None,
            [
                {"start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"start_date": "2021-01-03", "end_date": "2021-01-03"},
                {"start_date": "2021-01-04", "end_date": "2021-01-04"},
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
            ],
        ),
        (
            "test_start_end_min_max_inherits_datetime_format_from_stream_slicer",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10", max_datetime="{{ stream_state['date'] }}"),
            "1d",
            None,
            [
                {"start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"start_date": "2021-01-03", "end_date": "2021-01-03"},
                {"start_date": "2021-01-04", "end_date": "2021-01-04"},
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
            ],
        ),
    ],
)
def test_stream_slices(mock_datetime_now, test_name, stream_state, start, end, cursor, step, expected_slices):
    slicer = DatetimeStreamSlicer(start, end, step, cursor, datetime_format, config)
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


if __name__ == "__main__":
    unittest.main()
