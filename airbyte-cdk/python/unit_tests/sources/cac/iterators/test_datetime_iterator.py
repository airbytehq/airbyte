#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
import unittest

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator

FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01"}
start_date = {
    "value": "{{ stream_state['date'] }}",
    "default": "{{ config['start_date'] }}",
}
end_date_now = {
    "value": "{{ today_utc() }}",
}
end_date = {
    "value": "2021-01-10",
}
cursor_value = {"name": "date", "value": "{{ stream_state['start_date'] }}"}
vars = {}
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
    step = datetime.timedelta(days=1)
    iterator = DatetimeIterator(start_date, end_date, step, timezone, cursor_value, datetime_format, vars, config)
    stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)

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
    step = datetime.timedelta(days=2)
    iterator = DatetimeIterator(start_date, end_date, step, timezone, cursor_value, datetime_format, vars, config)
    stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)

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
    step = datetime.timedelta(days=1)
    iterator = DatetimeIterator(start_date, end_date, step, timezone, cursor_value, datetime_format, vars, config)
    stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


def test_stream_slices_12_days(mock_datetime_now):
    stream_state = None

    expected_slices = [
        {"start_date": "2021-01-01", "end_date": "2021-01-10"},
    ]
    step = datetime.timedelta(days=12)
    iterator = DatetimeIterator(start_date, end_date, step, timezone, cursor_value, datetime_format, vars, config)
    stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


def test_init_from_config(mock_datetime_now):
    step = datetime.timedelta(days=1)

    iterator = DatetimeIterator(start_date, end_date_now, step, timezone, cursor_value, datetime_format, vars, config)
    assert datetime.datetime(2021, 1, 1, tzinfo=timezone) == iterator._start_time
    assert FAKE_NOW == iterator._end_time
    assert datetime.timedelta(days=1) == iterator._step
    assert datetime.timezone.utc == iterator._timezone
    assert datetime_format == iterator._datetime_format


def test_end_date_past_now(mock_datetime_now):
    step = datetime.timedelta(days=1)
    invalid_end_date = {
        "value": f"{(FAKE_NOW + step).strftime(datetime_format)}",
    }
    iterator = DatetimeIterator(start_date, invalid_end_date, step, timezone, cursor_value, datetime_format, vars, config)

    assert iterator._end_time != invalid_end_date
    assert iterator._end_time == datetime.datetime.now()


def test_start_date_after_end_date():
    step = datetime.timedelta(days=1)
    invalid_start_date = {
        "value": "2021-01-11",
    }
    iterator = DatetimeIterator(invalid_start_date, end_date, step, timezone, cursor_value, datetime_format, vars, config)

    assert iterator._start_time != invalid_start_date
    assert iterator._start_time == iterator._end_time
    assert iterator._start_time == datetime.datetime(2021, 1, 10, tzinfo=datetime.timezone.utc)


if __name__ == "__main__":
    unittest.main()
