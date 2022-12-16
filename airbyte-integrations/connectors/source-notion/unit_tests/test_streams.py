#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import random
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_notion.streams import NotionStream, Users


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(NotionStream, "path", "v0/example_endpoint")
    mocker.patch.object(NotionStream, "primary_key", "test_primary_key")
    mocker.patch.object(NotionStream, "__abstractmethods__", set())


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
    expected_headers = {"Notion-Version": "2021-08-16"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = NotionStream(config=MagicMock())
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = NotionStream(config=MagicMock())
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock(headers={"retry-after": "10"})
    stream = NotionStream(config=MagicMock())
    assert stream.backoff_time(response_mock) == 10.0


def test_users_request_params(patch_base_class):
    stream = Users(config=MagicMock())

    # No next_page_token. First pull
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"page_size": 100}
    assert stream.request_params(**inputs) == expected_params

    # When getting pages after the first pull.
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"next_cursor": "123"}}
    expected_params = {"start_cursor": "123", "page_size": 100}
    assert stream.request_params(**inputs) == expected_params


def test_user_stream_handles_pagination_correclty(requests_mock):
    """
    Test shows that Users stream uses pagination as per Notion API docs.
    """

    response_body = {
        "object": "list",
        "results": [{"id": f"{x}", "object": "user", "type": ["person", "bot"][random.randint(0, 1)]} for x in range(100)],
        "next_cursor": "bc48234b-77b2-41a6-95a3-6a8abb7887d5",
        "has_more": True,
        "type": "user",
    }
    requests_mock.get("https://api.notion.com/v1/users?page_size=100", json=response_body)

    response_body = {
        "object": "list",
        "results": [{"id": f"{x}", "object": "user", "type": ["person", "bot"][random.randint(0, 1)]} for x in range(100, 200)],
        "next_cursor": "67030467-b97b-4729-8fd6-2fb33d012da4",
        "has_more": True,
        "type": "user",
    }
    requests_mock.get("https://api.notion.com/v1/users?page_size=100&start_cursor=bc48234b-77b2-41a6-95a3-6a8abb7887d5", json=response_body)

    response_body = {
        "object": "list",
        "results": [{"id": f"{x}", "object": "user", "type": ["person", "bot"][random.randint(0, 1)]} for x in range(200, 220)],
        "next_cursor": None,
        "has_more": False,
        "type": "user",
    }
    requests_mock.get("https://api.notion.com/v1/users?page_size=100&start_cursor=67030467-b97b-4729-8fd6-2fb33d012da4", json=response_body)

    stream = Users(config=MagicMock())

    records = stream.read_records(sync_mode=SyncMode.full_refresh)
    records_length = sum(1 for _ in records)
    assert records_length == 220
