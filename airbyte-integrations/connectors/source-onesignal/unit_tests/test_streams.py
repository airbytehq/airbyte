#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_onesignal.streams import OnesignalStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OnesignalStream, "path", "v0/example_endpoint")
    mocker.patch.object(OnesignalStream, "primary_key", "test_primary_key")
    mocker.patch.object(OnesignalStream, "__abstractmethods__", set())


@pytest.fixture
def stream(patch_base_class):
    args = {"authenticator": None, "config": {"user_auth_key": "", "start_date": "2021-01-01T00:00:00Z", "outcome_names": ""}}
    return OnesignalStream(**args)


def test_next_page_token(stream):
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(stream, requests_mock):
    requests_mock.get("https://dummy", json=[{"id": 123, "basic_auth_key": "xx"}])
    resp = requests.get("https://dummy")

    inputs = {"response": resp, "stream_state": MagicMock()}
    expected_parsed_object = {"id": 123, "basic_auth_key": "xx"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(stream):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(stream):
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
def test_should_retry(stream, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(stream):
    response_mock = MagicMock()
    expected_backoff_time = 60
    assert stream.backoff_time(response_mock) == expected_backoff_time
