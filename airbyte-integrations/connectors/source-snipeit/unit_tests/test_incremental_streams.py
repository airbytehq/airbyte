#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_snipeit.incremental_streams import Events


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Events, "path", "v0/example_endpoint")
    mocker.patch.object(Events, "primary_key", "test_primary_key")
    mocker.patch.object(Events, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = Events()
    expected_cursor_field = "updated_at/datetime"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = Events()
    # TODO: replace this with your input parameters
    inputs = {
        "current_stream_state": {
            "updated_at/datetime": "2022-04-20 19:06:42.805431+08:00"
        },
        "latest_record": {
            "updated_at": {
                "datetime": "2022-04-20 19:07:23.181174+08:00"
            }
        }
    }
    expected_state = {"updated_at/datetime": "2022-04-20 19:07:23.181174+08:00"}
    assert stream.get_updated_state(**inputs) == expected_state


# NOTE: Stream Slices not implemented. I'm excluding this test.
# def test_stream_slices(patch_incremental_base_class):
#     stream = Events()
#     # TODO: replace this with your input parameters
#     inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
#     # TODO: replace this with your expected stream slices list
#     expected_stream_slice = [None]
#     assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(Events, "cursor_field", "dummy_field")
    stream = Events()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = Events()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = Events()
    expected_checkpoint_interval = 10
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
