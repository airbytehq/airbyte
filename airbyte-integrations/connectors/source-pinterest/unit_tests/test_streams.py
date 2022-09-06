#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from source_pinterest.source import Boards, PinterestStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PinterestStream, "path", "v0/example_endpoint")
    mocker.patch.object(PinterestStream, "primary_key", "test_primary_key")
    mocker.patch.object(PinterestStream, "__abstractmethods__", set())
    #
    mocker.patch.object(PinterestSubStream, "path", "v0/example_endpoint")
    mocker.patch.object(PinterestSubStream, "primary_key", "test_primary_key")
    mocker.patch.object(PinterestSubStream, "next_page_token", None)
    mocker.patch.object(PinterestSubStream, "parse_response", {})
    mocker.patch.object(PinterestSubStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = PinterestStream(config=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, test_response):
    stream = PinterestStream(config=MagicMock())
    inputs = {"response": test_response}
    expected_token = {"bookmark": "string"}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, test_response, test_current_stream_state):
    stream = PinterestStream(config=MagicMock())
    inputs = {"response": test_response, "stream_state": test_current_stream_state}
    expected_parsed_object = {}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = PinterestStream(config=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = PinterestStream(config=MagicMock())
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, False),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = PinterestStream(config=MagicMock())
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = PinterestStream(config=MagicMock())
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_backoff_strategy_on_rate_limit_error(requests_mock):
    board_1 = {
        "id": "549755885175",
        "name": "Summer Recipes",
        "description": "My favorite summer recipes",
        "privacy": "PUBLIC"
    }
    board_2 = {
        "id": "549755885176",
        "name": "Crazy Cats",
        "description": "These cats are crazy",
        "privacy": "PUBLIC"
    }
    responses = [
        {
            "json": {"items": [board_1], "bookmark": "123"},
            "status_code": 200,
        },
        {
            "headers": {"X-RateLimit-Reset": "1"},
            "status_code": 429,
        },
        {
            "json": {"items": [board_2]},
            "status_code": 200,
        }
    ]
    requests_mock.register_uri("GET", "https://api.pinterest.com/v5/boards", responses)

    records = []
    for record in Boards(config=MagicMock()).read_records(sync_mode=SyncMode.full_refresh):
        records.append(record)

    assert board_1 in records
    assert board_2 in records
