#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_zendesk_sell.source import IncrementalZendeskSellStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalZendeskSellStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalZendeskSellStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalZendeskSellStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalZendeskSellStream()
    expected_cursor_field = "updated_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalZendeskSellStream()
    inputs = {"current_stream_state": {"updated_at": "2022-03-17T16:03:07Z"}, "latest_record": {"updated_at": "2022-03-18T16:03:07Z"}}
    expected_state = {"updated_at": "2022-03-18T16:03:07Z"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalZendeskSellStream()
    # TODO: replace this with your input parameters
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalZendeskSellStream, "cursor_field", "dummy_field")
    stream = IncrementalZendeskSellStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalZendeskSellStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalZendeskSellStream()
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
