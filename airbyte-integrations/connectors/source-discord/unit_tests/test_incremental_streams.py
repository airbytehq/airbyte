#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_discord.source import IncrementalDiscordStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalDiscordStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalDiscordStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalDiscordStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalDiscordStream()
    # TODO: replace this with your expected cursor field
    expected_cursor_field = []
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalDiscordStream()
    # TODO: replace this with your input parameters
    inputs = {"current_stream_state": None, "latest_record": None}
    # TODO: replace this with your expected updated stream state
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalDiscordStream()
    # TODO: replace this with your input parameters
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalDiscordStream, "cursor_field", "dummy_field")
    stream = IncrementalDiscordStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalDiscordStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalDiscordStream()
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
