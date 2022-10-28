#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_pagarme.streams import IncrementalPagarmeStream, Payables


@fixture
def test_current_stream_state():
    return {"date_created": "2021-10-22"}


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalPagarmeStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalPagarmeStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalPagarmeStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalPagarmeStream(api_key="key")
    expected_cursor_field = "date_created"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(test_current_stream_state):
    stream = Payables(api_key="key")
    inputs = {"current_stream_state": test_current_stream_state, "latest_record": test_current_stream_state}
    expected_state = {"date_created": "2021-10-22"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalPagarmeStream(api_key="key")
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalPagarmeStream, "cursor_field", "dummy_field")
    stream = IncrementalPagarmeStream(api_key="key")
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalPagarmeStream(api_key="key")
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalPagarmeStream(api_key="key")
    expected_checkpoint_interval = 1000
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
