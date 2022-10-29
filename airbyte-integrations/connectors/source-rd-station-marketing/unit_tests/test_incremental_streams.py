#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_rd_station_marketing.streams import IncrementalRDStationMarketingStream


@fixture
def test_current_stream_state():
    return {"updated_time": "2021-10-22"}


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalRDStationMarketingStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalRDStationMarketingStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalRDStationMarketingStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalRDStationMarketingStream(authenticator=MagicMock())
    expected_cursor_field = []
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, test_current_stream_state, mocker):
    mocker.patch.object(IncrementalRDStationMarketingStream, "cursor_field", "updated_time")
    stream = IncrementalRDStationMarketingStream(authenticator=MagicMock())
    inputs = {"current_stream_state": test_current_stream_state, "latest_record": test_current_stream_state}
    expected_state = {"updated_time": "2021-10-22"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalRDStationMarketingStream(authenticator=MagicMock())
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalRDStationMarketingStream, "cursor_field", "dummy_field")
    stream = IncrementalRDStationMarketingStream(authenticator=MagicMock())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalRDStationMarketingStream(authenticator=MagicMock())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalRDStationMarketingStream(authenticator=MagicMock())
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
