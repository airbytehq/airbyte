#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_vtex.base_streams import IncrementalVtexStream
from source_vtex.source import VtexAuthenticator


CURSOR_FIELD = 'creationDate'

def fake_authenticator():
    return VtexAuthenticator(
        'not', 'real', 'auth'
    )

def build_stream():
    start_date =  "2021-10-27T00:00:00.000Z"
    stream = IncrementalVtexStream(
        start_date=start_date,
        authenticator=fake_authenticator()
    )
    return stream

@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalVtexStream, "path", "v0/example_endpoint")
    mocker.patch.object(
        IncrementalVtexStream, "primary_key", "test_primary_key"
    )
    mocker.patch.object(IncrementalVtexStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = build_stream()
    
    expected_cursor_field = CURSOR_FIELD
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = build_stream()
    latest_date = {
        CURSOR_FIELD: '2021-10-28T23:33:05.0000000+00:00'
    }

    earliest_date = {
        CURSOR_FIELD: '2021-10-28T20:33:05.0000000+00:00'
    }
    
    inputs = {
        "current_stream_state": latest_date, 
        "latest_record": earliest_date
    }

    expected_state = latest_date

    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = build_stream()
    
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": CURSOR_FIELD, "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalVtexStream, "cursor_field", "dummy_field")
    stream = build_stream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = build_stream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = build_stream()
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
