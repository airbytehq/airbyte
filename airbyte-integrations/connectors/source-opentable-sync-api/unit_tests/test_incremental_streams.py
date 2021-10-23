#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_opentable_sync_api.source import OpentableSyncAPIStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OpentableSyncAPIStream, "path", "v0/example_endpoint")
    mocker.patch.object(OpentableSyncAPIStream, "primary_key", "test_primary_key")
    mocker.patch.object(OpentableSyncAPIStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your expected cursor field
    expected_cursor_field = []
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your input parameters
    inputs = {
        "current_stream_state": {"9999": "2021-10-10 10:10:10"},
        "latest_record": {"rid": "9999", "updated_at_utc": "2021-12-10T10:10:10Z"},
    }
    # TODO: replace this with your expected updated stream state
    expected_state = {"9999": "2021-12-10 10:10:10"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your input parameters
    inputs = {"sync_mode": SyncMode.incremental, "stream_state": {}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = yield {"rid": 10, "start_date": "2021-12-10T10:10:10Z"}
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, config):
    mocker.patch.object(OpentableSyncAPIStream, "cursor_field", "dummy_field")
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
