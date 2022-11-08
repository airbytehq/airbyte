#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import requests
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_onesignal.streams import Apps, Devices, IncrementalOnesignalStream, Notifications


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalOnesignalStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalOnesignalStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalOnesignalStream, "__abstractmethods__", set())


@fixture
def args():
    return {"authenticator": None, "config": {"user_auth_key": "", "start_date": "2021-01-01T00:00:00Z", "outcome_names": ""}}


@fixture
def parent(args):
    return Apps(**args)


@fixture
def stream(patch_incremental_base_class, parent, args):
    return IncrementalOnesignalStream(parent=parent, **args)


def test_cursor_field(stream):
    expected_cursor_field = "updated_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(stream):
    inputs = {"current_stream_state": {"updated_at": 42}, "latest_record": {"updated_at": 90}}
    expected_state = 90
    state = stream.get_updated_state(**inputs)
    assert state["updated_at"] == expected_state

    inputs = {"current_stream_state": state, "latest_record": {"updated_at": 100}}
    expected_state = 100
    state = stream.get_updated_state(**inputs)
    assert state["updated_at"] == expected_state

    # after stream sync is finished, state should output the max cursor time
    stream.is_finished = True
    inputs = {"current_stream_state": state, "latest_record": {"updated_at": 80}}
    expected_state = 100
    state = stream.get_updated_state(**inputs)
    assert state["updated_at"] == expected_state


def test_stream_slices(stream, requests_mock):
    requests_mock.get(
        "https://onesignal.com/api/v1/apps", json=[{"id": "abc", "basic_auth_key": "key 1"}, {"id": "def", "basic_auth_key": "key 2"}]
    )

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [{"app_id": "abc", "rest_api_key": "key 1"}, {"app_id": "def", "rest_api_key": "key 2"}]
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


def test_end_of_stream_state(parent, args, requests_mock):
    requests_mock.get(
        "https://onesignal.com/api/v1/apps",
        json=[{"id": "abc", "basic_auth_key": "key 1"}, {"id": "def", "basic_auth_key": "key 2"}, {"id": "ghi", "basic_auth_key": "key 3"}],
    )
    requests_mock.get(
        "https://onesignal.com/api/v1/notifications?app_id=abc",
        json={"total_count": 1, "offset": 0, "limit": 1, "notifications": [{"id": "notification 1", "queued_at": 90}]},
    )
    requests_mock.get(
        "https://onesignal.com/api/v1/notifications?app_id=def",
        json={"total_count": 1, "offset": 0, "limit": 1, "notifications": [{"id": "notification 2", "queued_at": 80}]},
    )
    requests_mock.get(
        "https://onesignal.com/api/v1/notifications?app_id=ghi",
        json={"total_count": 1, "offset": 0, "limit": 1, "notifications": [{"id": "notification 3", "queued_at": 70}]},
    )

    stream = Notifications(parent=parent, **args)
    state = {"queued_at": 50}
    sync_mode = SyncMode.incremental

    for idx, app_slice in enumerate(stream.stream_slices(sync_mode, **MagicMock())):
        for record in stream.read_records(sync_mode, stream_slice=app_slice):
            state = stream.get_updated_state(state, record)
            if idx == 2:  # the last slice
                assert state["queued_at"] == 90
            else:
                assert state["queued_at"] == 90


def test_supports_incremental(patch_incremental_base_class, mocker, parent, args):
    mocker.patch.object(IncrementalOnesignalStream, "cursor_field", "dummy_field")
    stream = IncrementalOnesignalStream(parent=parent, **args)
    assert stream.supports_incremental


def test_source_defined_cursor(stream):
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream):
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_next_page_token(stream, requests_mock):
    requests_mock.get("https://dummy", json={"total_count": 123, "offset": 22, "limit": 33})
    resp = requests.get("https://dummy")
    expected_next_page_token = {"offset": 55}
    assert stream.next_page_token(resp) == expected_next_page_token

    requests_mock.get("https://dummy", json={"total_count": 123, "offset": 100, "limit": 33})
    resp = requests.get("https://dummy")
    expected_next_page_token = None
    assert stream.next_page_token(resp) == expected_next_page_token


def test_request_params(stream, parent, args):
    inputs = {"stream_state": {}, "stream_slice": {"app_id": "abc"}}
    inputs2 = {"stream_state": {}, "stream_slice": {"app_id": "abc"}, "next_page_token": {"offset": 42}}
    expected_request_params = {"app_id": "abc", "limit": None}
    expected_request_params2 = {"app_id": "abc", "limit": None, "offset": 42}

    assert stream.request_params(**inputs) == expected_request_params
    assert stream.request_params(**inputs2) == expected_request_params2

    stream2 = Devices(parent=parent, **args)
    expected_request_params["limit"] = 300
    expected_request_params2["limit"] = 300
    assert stream2.request_params(**inputs) == expected_request_params
    assert stream2.request_params(**inputs2) == expected_request_params2

    stream3 = Notifications(parent=parent, **args)
    expected_request_params["limit"] = 50
    expected_request_params2["limit"] = 50
    assert stream3.request_params(**inputs) == expected_request_params
    assert stream3.request_params(**inputs2) == expected_request_params2


def test_filter_by_state(stream):
    inputs = {"stream_state": {"updated_at": 1580510247}, "record": {"updated_at": 1580510248}}
    expected_filter_by_state = True
    assert stream.filter_by_state(**inputs) == expected_filter_by_state

    inputs = {"stream_state": {"updated_at": 1580510248}, "record": {"updated_at": 1580510247}}
    expected_filter_by_state = False
    assert stream.filter_by_state(**inputs) == expected_filter_by_state
