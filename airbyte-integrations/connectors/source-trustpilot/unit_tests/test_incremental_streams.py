#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pendulum
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_trustpilot.streams import TrustpilotIncrementalStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(TrustpilotIncrementalStream, "path", "v0/example_endpoint")
    mocker.patch.object(TrustpilotIncrementalStream, "primary_key", "test_primary_key")
    mocker.patch.object(TrustpilotIncrementalStream, "_start_date",
                        pendulum.now("UTC").add(years=-1))
    mocker.patch.object(TrustpilotIncrementalStream, "_current_stream_slice",
                        {'business_unit_id': '5f5e954ec15b2700017c834f'})

    mocker.patch.object(TrustpilotIncrementalStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = TrustpilotIncrementalStream()
    expected_cursor_field = 'createdAt'
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = TrustpilotIncrementalStream()
    inputs = {
        "current_stream_state": {
            '5f5e954ec15b2700017c834f_createdAt': '2023-03-01T00:00:00+00:00'
        },
        "latest_record": {
            'createdAt': '2023-03-23T15:12:17Z'
        }
    }
    expected_state = {
        '5f5e954ec15b2700017c834f_createdAt': '2023-03-23T15:12:17+00:00'
    }
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = TrustpilotIncrementalStream()
    inputs = {
        "sync_mode": SyncMode.incremental,
        "cursor_field": [
            'createdAt'
        ],
        "stream_state": {
            '5f5e954ec15b2700017c834f_createdAt': '2023-03-01T00:00:00+00:00'
        }
    }
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(TrustpilotIncrementalStream, "cursor_field", "dummy_field")
    stream = TrustpilotIncrementalStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = TrustpilotIncrementalStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = TrustpilotIncrementalStream()
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
