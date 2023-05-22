#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.models import SyncMode


def test_cursor_field(stream):
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices(stream):
    stream.end_date = datetime.datetime(2023, 6, 1)
    start_date = datetime.datetime(2023, 4, 1)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "date", "stream_state": {"date": start_date.strftime("%Y-%m-%d")}}

    dates = [{'start_date': '2023-04-01', 'end_date': '2023-05-01'}, {'start_date': '2023-05-02', 'end_date': '2023-06-01'}]

    print(list(stream.stream_slices(**inputs)))
    assert list(stream.stream_slices(**inputs)) == dates


def test_supports_incremental(stream):
    assert stream.supports_incremental


def test_source_defined_cursor(stream):
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream):
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
