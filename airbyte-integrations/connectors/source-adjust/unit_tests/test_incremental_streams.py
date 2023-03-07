#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.models import SyncMode
from source_adjust.source import AdjustReportStream

CONFIG = {
    "ingest_start": "2022-07-01",
    "until_today": True,
}


def test_cursor_field():
    stream = AdjustReportStream(connector=None, config=CONFIG)
    expected_cursor_field = "day"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices():
    stream = AdjustReportStream(connector=None, config=CONFIG)
    period = 5
    start = datetime.date.today() - datetime.timedelta(days=period)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "day", "stream_state": {"day": start.isoformat()}}
    assert list(stream.stream_slices(**inputs)) == [{"day": (start + datetime.timedelta(days=d)).isoformat()} for d in range(period)]


def test_supports_incremental():
    stream = AdjustReportStream(connector=None, config=CONFIG)
    assert stream.supports_incremental


def test_source_defined_cursor():
    stream = AdjustReportStream(connector=None, config=CONFIG)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval():
    stream = AdjustReportStream(connector=None, config=CONFIG)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
