#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_xero.streams import IncrementalXeroStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalXeroStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalXeroStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalXeroStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalXeroStream(start_date=datetime.datetime.now())
    expected_cursor_field = "UpdatedDateUTC"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalXeroStream(start_date=datetime.datetime.now())
    date = datetime.datetime.now().replace(microsecond=0)
    inputs = {"current_stream_state": {"date": "2022-01-01"}, "latest_record": {"UpdatedDateUTC": date.isoformat()}}
    expected_state = {"date": date.isoformat()}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalXeroStream(start_date=datetime.datetime.now())
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalXeroStream, "cursor_field", "dummy_field")
    stream = IncrementalXeroStream(start_date=datetime.datetime.now())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalXeroStream(start_date=datetime.datetime.now())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalXeroStream(start_date=datetime.datetime.now())
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
