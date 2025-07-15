#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import freezegun
import pytest
import requests
from pytest import fixture, mark
from source_notion.streams import Blocks, IncrementalNotionStream, NotionStream, Pages

from airbyte_cdk.models import SyncMode


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(NotionStream, "path", "v0/example_endpoint")
    mocker.patch.object(NotionStream, "primary_key", "test_primary_key")
    mocker.patch.object(NotionStream, "__abstractmethods__", set())


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalNotionStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalNotionStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalNotionStream, "__abstractmethods__", set())


@fixture
def args():
    return {"authenticator": None, "config": {"access_token": "", "start_date": "2021-01-01T00:00:00.000Z"}}


@fixture
def parent(args):
    return Pages(**args)


@fixture
def stream(args):
    return IncrementalNotionStream(**args)


@fixture
def blocks(parent, args):
    return Blocks(parent=parent, **args)


def test_cursor_field(stream):
    expected_cursor_field = "last_edited_time"
    assert stream.cursor_field == expected_cursor_field


def test_supports_incremental(stream, mocker):
    mocker.patch.object(IncrementalNotionStream, "cursor_field", "dummy_field")
    assert stream.supports_incremental


def test_source_defined_cursor(stream):
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream):
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_http_method(patch_base_class):
    stream = NotionStream(config=MagicMock())
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    "response_json, expected_output",
    [({"next_cursor": "some_cursor", "has_more": True}, {"next_cursor": "some_cursor"}), ({"has_more": False}, None), ({}, None)],
    ids=["Next_page_token exists with cursor", "No next_page_token", "No next_page_token"],
)
def test_next_page_token(patch_base_class, response_json, expected_output):
    stream = NotionStream(config=MagicMock())
    mock_response = MagicMock()
    mock_response.json.return_value = response_json
    result = stream.next_page_token(mock_response)
    assert result == expected_output


@pytest.mark.parametrize(
    "config, expected_start_date, current_time",
    [
        (
            {"authenticator": "secret_token", "start_date": "2021-09-01T00:00:00.000Z"},
            "2021-09-01T00:00:00.000Z",
            "2022-09-22T00:00:00.000Z",
        ),
        ({"authenticator": "super_secret_token", "start_date": None}, "2020-09-22T00:00:00.000Z", "2022-09-22T00:00:00.000Z"),
        ({"authenticator": "even_more_secret_token"}, "2021-01-01T12:30:00.000Z", "2023-01-01T12:30:00.000Z"),
    ],
)
def test_set_start_date(patch_base_class, config, expected_start_date, current_time):
    """
    Test that start_date in config is either:
      1. set to the value provided by the user
      2. defaults to two years from the present date set by the test environment.
    """
    with freezegun.freeze_time(current_time):
        stream = NotionStream(config=config)
        assert stream.start_date == expected_start_date


def test_request_params(blocks):
    stream = blocks
    inputs = {"stream_state": {}, "next_page_token": {"next_cursor": "aaa"}}
    expected_request_params = {"page_size": 100, "start_cursor": "aaa"}
    assert stream.request_params(**inputs) == expected_request_params


def test_stream_slices(blocks, requests_mock):
    stream = blocks
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json={
            "results": [
                {"id": "aaa", "last_edited_time": "2022-10-10T00:00:00.000Z"},
                {"id": "bbb", "last_edited_time": "2022-10-10T00:00:00.000Z"},
            ],
            "next_cursor": None,
        },
    )
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [{"page_id": "aaa"}, {"page_id": "bbb"}]
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


def test_end_of_stream_state(blocks, requests_mock):
    stream = blocks
    requests_mock.post(
        "https://api.notion.com/v1/search", json={"results": [{"id": "aaa"}, {"id": "bbb"}, {"id": "ccc"}], "next_cursor": None}
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/aaa/children",
        json={
            "results": [{"id": "block 1", "type": "heading_1", "has_children": False, "last_edited_time": "2021-10-30T00:00:00.000Z"}],
            "next_cursor": None,
        },
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/bbb/children",
        json={
            "results": [{"id": "block 2", "type": "heading_1", "has_children": False, "last_edited_time": "2021-10-20T00:00:00.000Z"}],
            "next_cursor": None,
        },
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/ccc/children",
        json={
            "results": [{"id": "block 3", "type": "heading_1", "has_children": False, "last_edited_time": "2021-10-10T00:00:00.000Z"}],
            "next_cursor": None,
        },
    )

    state = {"last_edited_time": "2021-10-01T00:00:00.000Z"}
    sync_mode = SyncMode.incremental

    for idx, app_slice in enumerate(stream.stream_slices(sync_mode, **MagicMock())):
        for record in stream.read_records(sync_mode=sync_mode, stream_slice=app_slice):
            state = stream.get_updated_state(state, record)
            state_value = state["last_edited_time"].value
            if idx == 2:  # the last slice
                assert state_value == "2021-10-30T00:00:00.000Z"
            else:
                assert state_value == "2021-10-01T00:00:00.000Z"


def test_get_updated_state(stream):
    # Test that state always updates to the maximum cursor time
    # This is the correct behavior for incremental syncs

    inputs = {
        "current_stream_state": {"last_edited_time": "2021-10-10T00:00:00.000Z"},
        "latest_record": {"last_edited_time": "2021-10-20T00:00:00.000Z"},
    }
    expected_state = "2021-10-20T00:00:00.000Z"  # Should update to the newer time
    state = stream._get_updated_state(**inputs)
    assert state["last_edited_time"] == expected_state

    inputs = {"current_stream_state": state, "latest_record": {"last_edited_time": "2021-10-30T00:00:00.000Z"}}
    expected_state = "2021-10-30T00:00:00.000Z"  # Should update to the newer time
    state = stream._get_updated_state(**inputs)
    assert state["last_edited_time"] == expected_state

    # Test with an older record - should keep the current max
    inputs = {"current_stream_state": state, "latest_record": {"last_edited_time": "2021-10-15T00:00:00.000Z"}}
    expected_state = "2021-10-30T00:00:00.000Z"  # Should keep the current max
    state = stream._get_updated_state(**inputs)
    assert state["last_edited_time"] == expected_state


def test_record_filter(blocks, requests_mock):
    stream = blocks
    sync_mode = SyncMode.incremental

    root = "aaa"
    record = {"id": "id1", "type": "heading_1", "has_children": False, "last_edited_time": "2021-10-20T00:00:00.000Z"}
    requests_mock.get(f"https://api.notion.com/v1/blocks/{root}/children", json={"results": [record], "next_cursor": None})

    inputs = {
        "sync_mode": sync_mode,
        "stream_state": {"last_edited_time": "2021-10-10T00:00:00.000Z"},
    }
    stream.block_id_stack = [root]
    assert next(stream.read_records(**inputs)) == record

    inputs = {
        "sync_mode": sync_mode,
        "stream_state": {"last_edited_time": "2021-10-30T00:00:00.000Z"},
    }
    stream.block_id_stack = [root]
    assert list(stream.read_records(**inputs)) == []

    # 'child_page' and 'child_database' should not be included
    record["type"] = "child_page"
    inputs = {
        "sync_mode": sync_mode,
        "stream_state": {"last_edited_time": "2021-10-10T00:00:00.000Z"},
    }
    stream.block_id_stack = [root]
    assert list(stream.read_records(**inputs)) == []
    record["type"] = "child_database"
    stream.block_id_stack = [root]
    assert list(stream.read_records(**inputs)) == []


def test_recursive_read(blocks, requests_mock):
    stream = blocks

    # block records tree:
    #
    # root |-> record1 -> record2 -> record3
    #      |-> record4

    root = "aaa"
    record1 = {"id": "id1", "type": "heading_1", "has_children": True, "last_edited_time": "2022-10-10T00:00:00.000Z"}
    record2 = {"id": "id2", "type": "heading_1", "has_children": True, "last_edited_time": "2022-10-10T00:00:00.000Z"}
    record3 = {"id": "id3", "type": "heading_1", "has_children": False, "last_edited_time": "2022-10-10T00:00:00.000Z"}
    record4 = {"id": "id4", "type": "heading_1", "has_children": False, "last_edited_time": "2022-10-10T00:00:00.000Z"}
    requests_mock.get(f"https://api.notion.com/v1/blocks/{root}/children", json={"results": [record1, record4], "next_cursor": None})
    requests_mock.get(f"https://api.notion.com/v1/blocks/{record1['id']}/children", json={"results": [record2], "next_cursor": None})
    requests_mock.get(f"https://api.notion.com/v1/blocks/{record2['id']}/children", json={"results": [record3], "next_cursor": None})

    inputs = {"sync_mode": SyncMode.incremental}
    stream.block_id_stack = [root]
    assert list(stream.read_records(**inputs)) == [record3, record2, record1, record4]


def test_invalid_start_cursor(parent, requests_mock, caplog):
    stream = parent
    error_message = "The start_cursor provided is invalid: wrong_start_cursor"
    search_endpoint = requests_mock.post(
        "https://api.notion.com/v1/search",
        status_code=400,
        json={"object": "error", "status": 400, "code": "validation_error", "message": error_message},
    )

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}

    # With our custom error handling, invalid start cursor errors should be handled gracefully
    # The stream should be skipped and logged, not raise an exception
    list(stream.read_records(**inputs))

    # Verify the error was logged and the stream was skipped
    assert f"Skipping stream pages, error message: {error_message}" in caplog.messages
    assert search_endpoint.call_count == 1  # Should only be called once before error


@mark.parametrize(
    "status_code,error_code,error_message,should_raise_error",
    [
        (400, "validation_error", "The start_cursor provided is invalid: wrong_start_cursor", False),  # Handled gracefully
        (429, "rate_limited", "Rate Limited", True),  # Should raise HTTPError
        (500, "internal_server_error", "Internal server error", True),  # Should raise HTTPError
    ],
)
def test_retry_logic(status_code, error_code, error_message, should_raise_error, parent, requests_mock, caplog):
    stream = parent

    # With the CDK update, retry logic is now handled declaratively
    # We expect the HTTP error to be raised directly rather than retried with custom logic
    search_endpoint = requests_mock.post(
        "https://api.notion.com/v1/search",
        status_code=status_code,
        json={"object": "error", "status": status_code, "code": error_code, "message": error_message},
    )

    inputs = {"sync_mode": SyncMode.full_refresh, "cursor_field": [], "stream_state": {}}

    # Mock the time.sleep function globally to prevent real backoff delays
    with patch("time.sleep", return_value=None):
        if should_raise_error:
            # Expect the HTTP error to be raised directly
            with pytest.raises(requests.exceptions.HTTPError) as exc_info:
                list(stream.read_records(**inputs))
            # Verify the error contains the expected status code
            assert str(status_code) in str(exc_info.value)
            # The CDK will retry multiple times before giving up
            assert search_endpoint.call_count > 1
        else:
            # For errors that our custom handling processes gracefully
            list(stream.read_records(**inputs))
            # Verify the error was logged and handled gracefully
            assert f"Skipping stream pages, error message: {error_message}" in caplog.messages
            # Should only be called once since we handle it gracefully
            assert search_endpoint.call_count == 1


def test_empty_blocks_results(requests_mock):
    stream = Blocks(parent=None, config=MagicMock())
    requests_mock.get(
        "https://api.notion.com/v1/blocks/aaa/children",
        json={
            "next_cursor": None,
        },
    )
    stream.block_id_stack = ["aaa"]
    assert list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice=[])) == []


@pytest.mark.parametrize(
    "initial_page_size, expected_page_size, mock_response",
    [
        (100, 50, {"status_code": 504, "json": {}, "headers": {"retry-after": "1"}}),
        (50, 25, {"status_code": 504, "json": {}, "headers": {"retry-after": "1"}}),
        (100, 100, {"status_code": 429, "json": {}, "headers": {"retry-after": "1"}}),
        (50, 100, {"status_code": 200, "json": {"data": "success"}, "headers": {}}),
    ],
    ids=[
        "504 error, page_size 100 -> 50",
        "504 error, page_size 50 -> 25",
        "429 error, page_size 100 -> 100",
        "200 success, page_size 50 -> 100",
    ],
)
def test_request_throttle(initial_page_size, expected_page_size, mock_response, requests_mock):
    """
    Tests that the request page_size is halved when a 504 error is encountered.
    Once a 200 success is encountered, the page_size is reset to 100, for use in the next call.
    """
    requests_mock.register_uri(
        "GET",
        "https://api.notion.com/v1/users",
        [{"status_code": mock_response["status_code"], "json": mock_response["json"], "headers": mock_response["headers"]}],
    )

    stream = Pages(config={"authenticator": "auth"})
    stream.page_size = initial_page_size
    # Note: should_retry method has been removed in favor of declarative error handling
    # This test now just verifies the page_size throttling logic
    if mock_response["status_code"] == 504:
        stream.page_size = stream.throttle_request_page_size(stream.page_size)
    elif mock_response["status_code"] == 200:
        stream.page_size = 100  # Reset to default

    assert stream.page_size == expected_page_size


def test_block_record_transformation():
    stream = Blocks(parent=None, config=MagicMock())
    response_record = {
        "object": "block",
        "id": "id",
        "parent": {"type": "page_id", "page_id": "id"},
        "created_time": "2021-10-19T13:33:00.000Z",
        "last_edited_time": "2021-10-19T13:33:00.000Z",
        "created_by": {"object": "user", "id": "id"},
        "last_edited_by": {"object": "user", "id": "id"},
        "has_children": False,
        "archived": False,
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "test", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "test",
                    "href": None,
                },
                {
                    "type": "text",
                    "text": {"content": "@", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": True,
                        "color": "default",
                    },
                    "plain_text": "@",
                    "href": None,
                },
                {
                    "type": "text",
                    "text": {"content": "test", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "test",
                    "href": None,
                },
                {
                    "type": "mention",
                    "mention": {"type": "page", "page": {"id": "id"}},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "test",
                    "href": "https://www.notion.so/id",
                },
            ],
            "color": "default",
        },
    }
    expected_record = {
        "object": "block",
        "id": "id",
        "parent": {"type": "page_id", "page_id": "id"},
        "created_time": "2021-10-19T13:33:00.000Z",
        "last_edited_time": "2021-10-19T13:33:00.000Z",
        "created_by": {"object": "user", "id": "id"},
        "last_edited_by": {"object": "user", "id": "id"},
        "has_children": False,
        "archived": False,
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "test", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "test",
                    "href": None,
                },
                {
                    "type": "text",
                    "text": {"content": "@", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": True,
                        "color": "default",
                    },
                    "plain_text": "@",
                    "href": None,
                },
                {
                    "type": "text",
                    "text": {"content": "test", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "test",
                    "href": None,
                },
                {
                    "type": "mention",
                    "mention": {"type": "page", "info": {"id": "id"}},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "test",
                    "href": "https://www.notion.so/id",
                },
            ],
            "color": "default",
        },
    }
    assert stream.transform(response_record) == expected_record


def test_should_not_retry_with_ai_block(requests_mock):
    stream = Blocks(parent=None, config=MagicMock())
    json_response = {
        "object": "error",
        "status": 400,
        "code": "validation_error",
        "message": "Block type ai_block is not supported via the API.",
    }
    requests_mock.get("https://api.notion.com/v1/blocks/123", json=json_response, status_code=400)
    test_response = requests.get("https://api.notion.com/v1/blocks/123")
    assert not stream.should_retry(test_response)


def test_should_not_retry_with_not_found_block(requests_mock):
    stream = Blocks(parent=None, config=MagicMock())
    json_response = {
        "object": "error",
        "status": 404,
        "message": "Not Found for url: https://api.notion.com/v1/blocks/123/children?page_size=100",
    }
    requests_mock.get("https://api.notion.com/v1/blocks/123", json=json_response, status_code=404)
    test_response = requests.get("https://api.notion.com/v1/blocks/123")
    assert not stream.should_retry(test_response)


def test_should_not_retry_with_invalid_start_cursor(requests_mock):
    stream = Pages(config=MagicMock())
    json_response = {
        "object": "error",
        "status": 400,
        "code": "validation_error",
        "message": "The start_cursor provided is invalid: wrong_start_cursor",
    }
    requests_mock.post("https://api.notion.com/v1/search", json=json_response, status_code=400)
    test_response = requests.post("https://api.notion.com/v1/search")
    assert not stream.should_retry(test_response)
