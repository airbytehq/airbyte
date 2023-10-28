#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
import time
from unittest.mock import MagicMock, patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from pytest import fixture, mark
from source_notion.streams import Blocks, Comments, IncrementalNotionStream, Pages


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
def stream(patch_incremental_base_class, args):
    return IncrementalNotionStream(**args)


@fixture
def blocks(parent, args):
    return Blocks(parent=parent, **args)


@fixture
def comments(parent, args):
    return Comments(parent=parent, **args)


def test_cursor_field(stream):
    expected_cursor_field = "last_edited_time"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(stream):
    stream.is_finished = False

    inputs = {
        "current_stream_state": {"last_edited_time": "2021-10-10T00:00:00.000Z"},
        "latest_record": {"last_edited_time": "2021-10-20T00:00:00.000Z"},
    }
    expected_state = "2021-10-10T00:00:00.000Z"
    state = stream.get_updated_state(**inputs)
    assert state["last_edited_time"].value == expected_state

    inputs = {"current_stream_state": state, "latest_record": {"last_edited_time": "2021-10-30T00:00:00.000Z"}}
    state = stream.get_updated_state(**inputs)
    assert state["last_edited_time"].value == expected_state

    # after stream sync is finished, state should output the max cursor time
    stream.is_finished = True
    inputs = {"current_stream_state": state, "latest_record": {"last_edited_time": "2021-10-10T00:00:00.000Z"}}
    expected_state = "2021-10-30T00:00:00.000Z"
    state = stream.get_updated_state(**inputs)
    assert state["last_edited_time"].value == expected_state


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
    inputs = {"stream_state": {}, "next_page_token": {"next_cursor": "aaa"}}
    expected_request_params = {"page_size": 100, "start_cursor": "aaa"}
    assert stream.request_params(**inputs) == expected_request_params


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
    with patch.object(stream, "backoff_time", return_value=0.1):
        list(stream.read_records(**inputs))
        assert search_endpoint.call_count == 8
        assert f"Skipping stream pages, error message: {error_message}" in caplog.messages


@mark.parametrize(
    "status_code,error_code,error_message, expected_backoff_time",
    [
        (400, "validation_error", "The start_cursor provided is invalid: wrong_start_cursor", [10, 10, 10, 10, 10, 10, 10]),
        (429, "rate_limited", "Rate Limited", [5, 5, 5, 5, 5, 5, 5]),  # Retry-header is set to 5 seconds for test
        (500, "internal_server_error", "Internal server error", [5, 10, 20, 40, 80, 5, 10]),
    ],
)
def test_retry_logic(status_code, error_code, error_message, expected_backoff_time, parent, requests_mock, caplog):
    stream = parent

    # Set up a generator that alternates between error and success responses, to check the reset of backoff time between failures
    mock_responses = (
        [
            {
                "status_code": status_code,
                "response": {"object": "error", "status": status_code, "code": error_code, "message": error_message},
            }
            for _ in range(5)
        ]
        + [{"status_code": 200, "response": {"object": "list", "results": [], "has_more": True, "next_cursor": "dummy_cursor"}}]
        + [
            {
                "status_code": status_code,
                "response": {"object": "error", "status": status_code, "code": error_code, "message": error_message},
            }
            for _ in range(2)
        ]
        + [{"status_code": 200, "response": {"object": "list", "results": [], "has_more": False, "next_cursor": None}}]
    )

    def response_callback(request, context):
        # Get the next response from the mock_responses list
        response = mock_responses.pop(0)
        context.status_code = response["status_code"]
        return response["response"]

    # Mock the time.sleep function to avoid waiting during tests
    with patch.object(time, "sleep", return_value=None):
        search_endpoint = requests_mock.post(
            "https://api.notion.com/v1/search",
            json=response_callback,
            headers={"retry-after": "5"},
        )

        inputs = {"sync_mode": SyncMode.full_refresh, "cursor_field": [], "stream_state": {}}
        try:
            list(stream.read_records(**inputs))
        except (UserDefinedBackoffException, DefaultBackoffException) as e:
            return e

        # Check that the endpoint was called the expected number of times
        assert search_endpoint.call_count == 9

        # Additional assertions to check reset of backoff time
        # Find the backoff times from the message logs to compare against expected backoff times
        log_messages = [record.message for record in caplog.records]
        backoff_times = [
            round(float(re.search(r"(\d+(\.\d+)?) seconds", msg).group(1)))
            for msg in log_messages
            if any(word in msg for word in ["Sleeping", "Waiting"])
        ]

        assert backoff_times == expected_backoff_time, f"Unexpected backoff times: {backoff_times}"


# Tests for Comments stream
def test_comments_path(comments):
    assert comments.path() == "comments"


def test_comments_request_params(comments):
    """
    Test that the request_params function returns the correct parameters for the Comments endpoint
    """
    params = comments.request_params(
        next_page_token=None, stream_slice={"block_id": "block1", "page_last_edited_time": "2021-01-01T00:00:00.000Z"}
    )

    assert params == {"block_id": "block1", "page_size": comments.page_size}


def test_comments_stream_slices(comments, requests_mock):
    """
    Test that the stream_slices function returns the parent page ids as "block_id" and the last edited time as "page_last_edited_time"
    """

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": comments.cursor_field, "stream_state": {}}

    requests_mock.post(
        "https://api.notion.com/v1/search",
        json={
            "results": [
                {"name": "page_1", "id": "id_1", "last_edited_time": "2021-01-01T00:00:00.000Z"},
                {"name": "page_2", "id": "id_2", "last_edited_time": "2021-20-01T00:00:00.000Z"},
            ],
            "next_cursor": None,
        },
    )

    expected_stream_slice = [
        {"block_id": "id_1", "page_last_edited_time": "2021-01-01T00:00:00.000Z"},
        {"block_id": "id_2", "page_last_edited_time": "2021-20-01T00:00:00.000Z"},
    ]

    actual_stream_slices_list = list(comments.stream_slices(**inputs))
    assert actual_stream_slices_list == expected_stream_slice


@mark.parametrize(
    "stream_slice, stream_state, mock_data, expected_records",
    [
        # Test that comments with page_last_edited_time >= stream_state are replicated, regardless of each record's LMD
        (
            {"block_id": "block_id_1", "page_last_edited_time": "2023-10-10T00:00:00.000Z"},
            {"page_last_edited_time": "2021-10-10T00:00:00.000Z"},
            [
                {
                    "id": "comment_id_1",
                    "rich_text": [{"type": "text", "text": {"content": "I am the Alpha comment"}}],
                    "last_edited_time": "2021-01-01T00:00:00.000Z",
                },
                {
                    "id": "comment_id_2",
                    "rich_text": [{"type": "text", "text": {"content": "I am the Omega comment"}}],
                    "last_edited_time": "2022-12-31T00:00:00.000Z",
                },
            ],
            [
                {
                    "id": "comment_id_1",
                    "rich_text": [{"type": "text", "text": {"content": "I am the Alpha comment"}}],
                    "last_edited_time": "2021-01-01T00:00:00.000Z",
                    "page_last_edited_time": "2023-10-10T00:00:00.000Z",
                },
                {
                    "id": "comment_id_2",
                    "rich_text": [{"type": "text", "text": {"content": "I am the Omega comment"}}],
                    "last_edited_time": "2022-12-31T00:00:00.000Z",
                    "page_last_edited_time": "2023-10-10T00:00:00.000Z",
                },
            ],
        ),
        # Test that comments with page_last_edited_time < stream_state are not replicated, regardless of each record's LMD
        (
            {"block_id": "block_id_2", "page_last_edited_time": "2021-01-01T00:00:00.000Z"},
            {"page_last_edited_time": "2022-20-20T00:00:00.000Z"},
            [
                {
                    "id": "comment_id_1",
                    "rich_text": [{"type": "text", "text": {"content": "I will not be replicated"}}],
                    "last_edited_time": "2021-10-30T00:00:00.000Z",
                },
                {
                    "id": "comment_id_2",
                    "rich_text": [{"type": "text", "text": {"content": "I will also not be replicated"}}],
                    "last_edited_time": "2023-01-01T00:00:00.000Z",
                },
            ],
            [],
        ),
    ],
)
def test_comments_read_records(comments, requests_mock, stream_slice, stream_state, mock_data, expected_records):
    inputs = {
        "sync_mode": SyncMode.incremental,
        "cursor_field": comments.cursor_field,
        "stream_state": stream_state,
        "stream_slice": stream_slice,
    }

    requests_mock.get(
        f"https://api.notion.com/v1/comments?block_id={stream_slice['block_id']}", json={"results": mock_data, "next_cursor": None}
    )

    response = list(comments.read_records(**inputs))
    assert response == expected_records
