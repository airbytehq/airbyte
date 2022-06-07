#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import unittest

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer

FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01"}
start_date = InterpolatedString("{{ stream_state['date'] }}", "{{ config['start_date'] }}")
end_date_now = InterpolatedString(
    "{{ today_utc() }}",
)
end_date = InterpolatedString("2021-01-10")
cursor_value = InterpolatedString("{{ stream_state['date'] }}")
timezone = datetime.timezone.utc

datetime_format = "%Y-%m-%d"


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    datetime_mock = unittest.mock.MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_NOW
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


def test_stream_slices_1_day(mock_datetime_now):
    stream_state = None

    expected_slices = [
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
    ]
    step = "1d"
    slicer = DatetimeStreamSlicer(start_date, end_date, step, cursor_value, datetime_format, config)
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


def test_stream_slices_2_days(mock_datetime_now):
    stream_state = None

    expected_slices = [
        {"start_date": "2021-01-01", "end_date": "2021-01-02"},
        {"start_date": "2021-01-03", "end_date": "2021-01-04"},
        {"start_date": "2021-01-05", "end_date": "2021-01-06"},
        {"start_date": "2021-01-07", "end_date": "2021-01-08"},
        {"start_date": "2021-01-09", "end_date": "2021-01-10"},
    ]
    step = "2d"
    slicer = DatetimeStreamSlicer(start_date, end_date, step, cursor_value, datetime_format, config)
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


def test_stream_slices_from_stream_state(mock_datetime_now):
    stream_state = {"date": "2021-01-05"}

    expected_slices = [
        # FIXME: should this include 2021-01-05?
        {"start_date": "2021-01-05", "end_date": "2021-01-05"},
        {"start_date": "2021-01-06", "end_date": "2021-01-06"},
        {"start_date": "2021-01-07", "end_date": "2021-01-07"},
        {"start_date": "2021-01-08", "end_date": "2021-01-08"},
        {"start_date": "2021-01-09", "end_date": "2021-01-09"},
        {"start_date": "2021-01-10", "end_date": "2021-01-10"},
    ]
    step = "1d"
    slicer = DatetimeStreamSlicer(start_date, end_date, step, cursor_value, datetime_format, config)
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


def test_stream_slices_12_days(mock_datetime_now):
    stream_state = None

    expected_slices = [
        {"start_date": "2021-01-01", "end_date": "2021-01-10"},
    ]
    step = "12d"
    slicer = DatetimeStreamSlicer(start_date, end_date, step, cursor_value, datetime_format, config)
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


def test_init_from_config(mock_datetime_now):
    step = "1d"

    slicer = DatetimeStreamSlicer(start_date, end_date_now, step, cursor_value, datetime_format, config)
    assert datetime.datetime(2021, 1, 1, tzinfo=timezone) == slicer._start_time
    assert FAKE_NOW == slicer._end_time
    assert datetime.timedelta(days=1) == slicer._step
    assert datetime.timezone.utc == slicer._timezone
    assert datetime_format == slicer._datetime_format


def test_end_date_past_now(mock_datetime_now):
    step = "1d"
    invalid_end_date = InterpolatedString(
        f"{(FAKE_NOW + datetime.timedelta(days=1)).strftime(datetime_format)}",
    )
    slicer = DatetimeStreamSlicer(start_date, invalid_end_date, step, cursor_value, datetime_format, config)

    assert slicer._end_time != invalid_end_date
    assert slicer._end_time == datetime.datetime.now()


def test_start_date_after_end_date():
    step = "1d"
    invalid_start_date = InterpolatedString("2021-01-11")
    slicer = DatetimeStreamSlicer(invalid_start_date, end_date, step, cursor_value, datetime_format, config)

    assert slicer._start_time != invalid_start_date
    assert slicer._start_time == slicer._end_time
    assert slicer._start_time == datetime.datetime(2021, 1, 10, tzinfo=datetime.timezone.utc)


if __name__ == "__main__":
    unittest.main()
