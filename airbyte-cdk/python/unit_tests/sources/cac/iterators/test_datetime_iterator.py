#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
import unittest

import pytest
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator

FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01"}
start_date = {
    "value": "{{ stream_state['date'] }}",
    "default": "{{ config['start_date'] }}",
}
end_date = {
    "value": "{{ today_utc() }}",
}
values = [{"name": "date", "value": "{{ stream_state['date'] }}"}]


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    datetime_mock = unittest.mock.MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_NOW
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


def test_date_1_day_chunks():
    """
    FIXME
    start_date = {
        "value": "{{ stream_state['date'] }}",
        "default": "{{ config['start_date'] }}",
    }
    end_date = {
        "value": "{{ DatetimeIterator.NOW }}",
    }
    values = [
        {"name": "date",
         "value": "{{ stream_state['date'] }}"}
    ]
    step = datetime.timedelta(days=1)
    timezone = datetime.timezone.utc
    vars = {}
    config = {}
    datetime_format = "%Y-%m-%d"
    iterator = DatetimeIterator(start_date, end_date, step, timezone, values, datetime_format, vars, config)
    stream_state = None
    stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)
    self.assertEqual(len(stream_slices), 366)
    """


def test_date_1_month_chunks():
    """
    FIXME
    start_date = datetime.datetime(2021, 1, 1)
    end_date = datetime.datetime(2022, 1, 1)
    step = datetime.timedelta(days=30)
    timezone = datetime.timezone.utc
    vars = {}
    config = {}
    iterator = DatetimeIterator(start_date, end_date, step, timezone, vars, config)
    stream_state = None
    stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)
    self.assertEqual(len(stream_slices), 13)
    """


def test_init_from_config(mock_datetime_now):
    step = datetime.timedelta(days=1)
    timezone = datetime.timezone.utc
    vars = {}
    datetime_format = "%Y-%m-%d"
    iterator = DatetimeIterator(start_date, end_date, step, timezone, values, datetime_format, vars, config)
    assert datetime.datetime(2021, 1, 1, tzinfo=timezone) == iterator._start_time
    assert FAKE_NOW == iterator._end_time
    assert datetime.timedelta(days=1) == iterator._step
    assert datetime.timezone.utc == iterator._timezone
    assert datetime_format == iterator._datetime_format


def test_end_date_past_now():
    # FIXME: add a test where end_date is past datetime.now()
    pass


def test_start_date_after_end_date():
    # FIXME: add a test where start_date is past end_date
    pass


if __name__ == "__main__":
    unittest.main()
