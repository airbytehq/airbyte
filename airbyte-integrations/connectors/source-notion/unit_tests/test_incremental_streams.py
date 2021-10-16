#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import requests
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_notion.streams import IncrementalNotionStream, Pages, Blocks


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalNotionStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalNotionStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalNotionStream, "__abstractmethods__", set())


@fixture
def args():
    return {
        "authenticator": None,
        "config": {
            "access_token": "",
            "start_date": "2021-01-01T00:00:00.000Z"
        }
    }


@fixture
def parent(args):
    return Pages(**args)


@fixture
def stream(patch_incremental_base_class, args):
    return IncrementalNotionStream(**args)


@fixture
def blocks(parent, args):
    return Blocks(parent=parent, **args)


def test_cursor_field(stream):
    expected_cursor_field = "last_edited_time"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(stream):
    inputs = {
        "current_stream_state": { "last_edited_time": "2021-10-10T00:00:00.000Z" },
        "latest_record": { "last_edited_time": "2021-10-20T00:00:00.000Z" }
    }
    expected_state = { "last_edited_time": "2021-10-20T00:00:00.000Z" }
    assert stream.get_updated_state(**inputs) == expected_state

    inputs = {
        "current_stream_state": { "last_edited_time": "2021-10-20T00:00:00.000Z" },
        "latest_record": { "last_edited_time": "2021-10-10T00:00:00.000Z" }
    }
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(blocks, requests_mock):
    stream = blocks
    requests_mock.post("https://api.notion.com/v1/search", json={
        "results": [ { "id": "aaa" }, { "id": "bbb" } ],
        "next_cursor": None
    })
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [ { "page_id": "aaa" }, { "page_id": "bbb" } ]
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


def test_supports_incremental(stream, mocker):
    mocker.patch.object(IncrementalNotionStream, "cursor_field", "dummy_field")
    assert stream.supports_incremental


def test_source_defined_cursor(stream):
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream):
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_request_params(blocks):
    stream = blocks
    inputs = { "stream_state": {}, "next_page_token": { "next_cursor": "aaa" } }
    expected_request_params = { "page_size": 100, "start_cursor": "aaa" }
    assert stream.request_params(**inputs) == expected_request_params


def test_filter_by_state(stream):
    inputs = {
        "stream_state": { "last_edited_time": "2021-10-10T00:00:00.000Z" },
        "record": { "last_edited_time": "2021-10-20T00:00:00.000Z" }
    }
    expected_filter_by_state  = [{ "last_edited_time": "2021-10-20T00:00:00.000Z" }]
    assert list(stream.filter_by_state(**inputs)) == expected_filter_by_state

    inputs = {
        "stream_state": { "last_edited_time": "2021-10-20T00:00:00.000Z" },
        "record": { "last_edited_time": "2021-10-10T00:00:00.000Z" }
    }
    expected_filter_by_state = []
    assert list(stream.filter_by_state(**inputs)) == expected_filter_by_state


def test_filter_by_state_blocks(blocks):
    stream = blocks

    inputs = {
        "stream_state": { "last_edited_time": "2021-10-10T00:00:00.000Z" },
        "record": { "last_edited_time": "2021-10-20T00:00:00.000Z", "type": "aaa" }
    }
    expected_filter_by_state  = [{ "last_edited_time": "2021-10-20T00:00:00.000Z", "type": "aaa" }]
    assert list(stream.filter_by_state(**inputs)) == expected_filter_by_state

    inputs = {
        "stream_state": { "last_edited_time": "2021-10-20T00:00:00.000Z" },
        "record": { "last_edited_time": "2021-10-10T00:00:00.000Z", "type": "aaa" }
    }
    expected_filter_by_state  = []
    assert list(stream.filter_by_state(**inputs)) == expected_filter_by_state

    # 'child_page' and 'child_database' should not be included
    inputs = {
        "stream_state": { "last_edited_time": "2021-10-10T00:00:00.000Z" },
        "record": { "last_edited_time": "2021-10-20T00:00:00.000Z", "type": "child_page" }
    }
    expected_filter_by_state = []
    assert list(stream.filter_by_state(**inputs)) == expected_filter_by_state
    inputs = {
        "stream_state": { "last_edited_time": "2021-10-10T00:00:00.000Z" },
        "record": { "last_edited_time": "2021-10-20T00:00:00.000Z", "type": "child_database" }
    }
    expected_filter_by_state = []
    assert list(stream.filter_by_state(**inputs)) == expected_filter_by_state
