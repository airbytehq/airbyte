#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_netsuite.source import IncrementalNetsuiteStream, SourceNetsuite

config = {
    "consumer_key": "consumer_key",
    "consumer_secret": "consumer_secret",
    "token_id": "token_id",
    "token_secret": "token_secret",
    "realm": "12345",
}

def make_stream():
    src = SourceNetsuite()
    auth = src.auth(config)
    url = src.record_url(config)
    return IncrementalNetsuiteStream(auth, "invoice", url)

@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalNetsuiteStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalNetsuiteStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalNetsuiteStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = make_stream()
    expected_cursor_field = "lastModifiedDate"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = make_stream()
    inputs = {"current_stream_state": {"lastModifiedDate": "2022-01-01T00:00:00.000Z"}, "latest_record": {"lastModifiedDate": "2021-12-31T23:59:59.999Z"}}
    expected_state = {"lastModifiedDate": "2022-01-01T00:00:00.000Z"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalNetsuiteStream, "cursor_field", "dummy_field")
    stream = make_stream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = make_stream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = make_stream()
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
