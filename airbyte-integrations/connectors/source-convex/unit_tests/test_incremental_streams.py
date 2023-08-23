#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_convex.source import ConvexStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ConvexStream, "path", "v0/example_endpoint")
    mocker.patch.object(ConvexStream, "primary_key", "test_primary_key")
    mocker.patch.object(ConvexStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    expected_cursor_field = "_ts"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 123}], "cursor": 1234, "snapshot": 3000, "hasMore": True}
    resp.status_code = 200
    stream.parse_response(resp, {})
    stream.next_page_token(resp)
    assert stream.get_updated_state(None, None) == {
        "snapshot_cursor": 1234,
        "snapshot_has_more": True,
        "delta_cursor": 3000,
    }
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1235}], "cursor": 1235, "snapshot": 3000, "hasMore": False}
    stream.parse_response(resp, {})
    stream.next_page_token(resp)
    assert stream.get_updated_state(None, None) == {
        "snapshot_cursor": 1235,
        "snapshot_has_more": False,
        "delta_cursor": 3000,
    }
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1235}], "cursor": 8000, "hasMore": True}
    stream.parse_response(resp, {})
    stream.next_page_token(resp)
    assert stream.get_updated_state(None, None) == {
        "snapshot_cursor": 1235,
        "snapshot_has_more": False,
        "delta_cursor": 8000,
    }
    assert stream._delta_has_more is True
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1235}], "cursor": 9000, "hasMore": False}
    stream.parse_response(resp, {})
    stream.next_page_token(resp)
    assert stream.get_updated_state(None, None) == {
        "snapshot_cursor": 1235,
        "snapshot_has_more": False,
        "delta_cursor": 9000,
    }
    assert stream._delta_has_more is False


def test_stream_slices(patch_incremental_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(ConvexStream, "cursor_field", "dummy_field")
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    expected_checkpoint_interval = 128
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
