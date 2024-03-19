#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import freezegun
from http import HTTPStatus
import pytest
from pytest import fixture, mark
import re
import requests
import time
from unittest.mock import MagicMock, patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from source_notion.streams import Blocks, IncrementalNotionStream, NotionStream, Pages



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


def test_request_params(patch_base_class):
    stream = NotionStream(config=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, requests_mock):
    stream = NotionStream(config=MagicMock())
    requests_mock.get("https://dummy", json={"next_cursor": "aaa"})
    inputs = {"response": requests.get("https://dummy")}
    expected_token = {"next_cursor": "aaa"}
    assert stream.next_page_token(**inputs) == expected_token


@pytest.mark.parametrize(
    "response_json, expected_output",
    [({"next_cursor": "some_cursor", "has_more": True}, {"next_cursor": "some_cursor"}), ({"has_more": False}, None), ({}, None)],
)
def test_next_page_token_with_no_cursor(patch_base_class, response_json, expected_output):
    stream = NotionStream(config=MagicMock())
    mock_response = MagicMock()
    mock_response.json.return_value = response_json
    result = stream.next_page_token(mock_response)
    assert result == expected_output


def test_parse_response(patch_base_class, requests_mock):
    stream = NotionStream(config=MagicMock())
    requests_mock.get("https://dummy", json={"results": [{"a": 123}, {"b": "xx"}]})
    resp = requests.get("https://dummy")
    inputs = {"response": resp, "stream_state": MagicMock()}
    expected_parsed_object = [{"a": 123}, {"b": "xx"}]
    assert list(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = NotionStream(config=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Notion-Version": "2022-06-28"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = NotionStream(config=MagicMock())
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, True),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        (HTTPStatus.BAD_GATEWAY, True),
        (HTTPStatus.FORBIDDEN, False),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = NotionStream(config=MagicMock())
    assert stream.should_retry(response_mock) == should_retry


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
    "status_code,retry_after_header,expected_backoff",
    [
        (429, "10", 10.0),  # Case for 429 error with retry-after header
        (429, None, 5.0),  # Case for 429 error without retry-after header, should default to 5.0
        (504, None, None),  # Case for 500-level error, should default to None and use CDK exponential backoff
        (400, None, 10.0),  # Case for specific 400-level error handled by check_invalid_start_cursor
    ],
)
def test_backoff_time(status_code, retry_after_header, expected_backoff, patch_base_class):
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = status_code
    response_mock.headers = {"retry-after": retry_after_header} if retry_after_header else {}
    stream = NotionStream(config=MagicMock())

    assert stream.backoff_time(response_mock) == expected_backoff


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
