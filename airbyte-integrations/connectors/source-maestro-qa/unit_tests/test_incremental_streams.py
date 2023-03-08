#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_maestro_qa.source import IncrementalMaestroQAStream

default_start_date = "2021-01-01T00:00:00Z"

@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalMaestroQAStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalMaestroQAStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalMaestroQAStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalMaestroQAStream(default_start_date=default_start_date)
    expected_cursor_field = "last_synced_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalMaestroQAStream(default_start_date=default_start_date)
    # TODO: replace this with your input parameters
    inputs = {"current_stream_state": None, "latest_record": None}
    # TODO: replace this with your expected updated stream state
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalMaestroQAStream, "cursor_field", "dummy_field")
    stream = IncrementalMaestroQAStream(default_start_date=default_start_date)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalMaestroQAStream(default_start_date=default_start_date)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalMaestroQAStream(default_start_date=default_start_date)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
