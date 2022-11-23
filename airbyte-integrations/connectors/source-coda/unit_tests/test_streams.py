#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_coda.source import CodaStream

logger = logging.getLogger()
logger.level = logging.DEBUG


authenticator = TokenAuthenticator(token="test_token"),


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CodaStream, "path", "v0/example_endpoint")
    mocker.patch.object(CodaStream, "primary_key", "test_primary_key")
    mocker.patch.object(CodaStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = CodaStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"limit": 25}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = CodaStream(authenticator=authenticator)
    response = MagicMock()
    response.json.return_value = {
       "id": "1244fds",
       "name": "Test doc"
    }
    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = CodaStream(authenticator=authenticator)

    response = MagicMock()
    response.json = MagicMock(return_value={'items': [{"id": 101}]})

    inputs = {"response": response}
    expected_parsed_object = response.json()['items'][0]
    assert next(iter(stream.parse_response(**inputs))) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = CodaStream(authenticator=authenticator)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = CodaStream(authenticator=authenticator)
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
    stream = CodaStream(authenticator=authenticator)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = CodaStream(authenticator=authenticator)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
