#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_outreach.source import IncrementalOutreachStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalOutreachStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalOutreachStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalOutreachStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalOutreachStream(authenticator=MagicMock())
    expected_cursor_field = "updatedAt"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalOutreachStream(authenticator=MagicMock(), start_date="2021-10-27T00:00:00.000Z")
    inputs = {"current_stream_state": {}, "latest_record": {}}
    expected_state = {"updatedAt": "2021-10-27T00:00:00.000Z"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalOutreachStream(authenticator=MagicMock())
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalOutreachStream, "cursor_field", "dummy_field")
    stream = IncrementalOutreachStream(authenticator=MagicMock())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalOutreachStream(authenticator=MagicMock())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalOutreachStream(authenticator=MagicMock())
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
