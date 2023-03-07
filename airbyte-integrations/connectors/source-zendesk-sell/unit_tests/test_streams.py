#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_zendesk_sell.source import ZendeskSellStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ZendeskSellStream, "path", "v0/example_endpoint")
    mocker.patch.object(ZendeskSellStream, "primary_key", "test_primary_key")
    mocker.patch.object(ZendeskSellStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ZendeskSellStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    ("inputs", "expected_token"),
    [
        (
            {
                "items": [],
                "meta": {
                    "type": "collection",
                    "count": 25,
                    "links": {
                        "self": "https://api.getbase.com/v2/contacts?page=2&per_page=25",
                        "first_page": "https://api.getbase.com/v2/contacts?page=1&per_page=25",
                        "prev_page": "https://api.getbase.com/v2/contacts?page=1&per_page=25",
                        "next_page": "https://api.getbase.com/v2/contacts?page=3&per_page=25",
                    },
                },
            },
            {"page": 3},
        ),
        (
            {
                "items": [],
                "meta": {
                    "type": "collection",
                    "count": 25,
                    "links": {
                        "self": "https://api.getbase.com/v2/contacts?page=2&per_page=25",
                        "first_page": "https://api.getbase.com/v2/contacts?page=1&per_page=25",
                        "prev_page": "https://api.getbase.com/v2/contacts?page=1&per_page=25",
                    },
                },
            },
            None,
        ),
        ({None}, None),
    ],
)
def test_next_page_token(mocker, requests_mock, patch_base_class, inputs, expected_token):
    stream = ZendeskSellStream()
    response = mocker.MagicMock()
    response.json.return_value = inputs
    assert stream.next_page_token(response) == expected_token


def test_parse_response(patch_base_class, mocker):
    stream = ZendeskSellStream()
    response = mocker.MagicMock()
    response.json.return_value = {
        "items": [
            {
                "data": {
                    "id": 302488228,
                    "creator_id": 2393211,
                    "contact_id": 302488227,
                    "created_at": "2020-11-12T09:05:47Z",
                    "updated_at": "2022-03-23T16:53:22Z",
                    "title": None,
                    "name": "Octavia Squidington",
                    "first_name": "Octavia",
                    "last_name": "Squidington",
                },
                "meta": {"version": 36, "type": "contact"},
            }
        ],
        "meta": {
            "type": "collection",
            "count": 25,
            "links": {
                "self": "https://api.getbase.com/v2/contacts?page=2&per_page=25",
                "first_page": "https://api.getbase.com/v2/contacts?page=1&per_page=25",
                "prev_page": "https://api.getbase.com/v2/contacts?page=1&per_page=25",
                "next_page": "https://api.getbase.com/v2/contacts?page=3&per_page=25",
            },
        },
    }
    expected_parsed_object = {
        "id": 302488228,
        "creator_id": 2393211,
        "contact_id": 302488227,
        "created_at": "2020-11-12T09:05:47Z",
        "updated_at": "2022-03-23T16:53:22Z",
        "title": None,
        "name": "Octavia Squidington",
        "first_name": "Octavia",
        "last_name": "Squidington",
    }
    assert next(stream.parse_response(response)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = ZendeskSellStream()
    stream_slice = None
    stream_state = None
    next_page_token = {"page": 2}
    expected_headers = {"page": 2}
    assert stream.request_params(stream_slice, stream_state, next_page_token) == expected_headers


def test_http_method(patch_base_class):
    stream = ZendeskSellStream()
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
    stream = ZendeskSellStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = ZendeskSellStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
