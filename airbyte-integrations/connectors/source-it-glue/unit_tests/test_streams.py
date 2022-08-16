#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_it_glue.source import ItGlueStream

# from urllib import response


@pytest.fixture()
def config(request):
    args = {"api_key": "YXNmnhkjf", "fatId": "12345"}
    return args


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ItGlueStream, "path", "v0/example_endpoint")
    mocker.patch.object(ItGlueStream, "primary_key", "test_primary_key")
    mocker.patch.object(ItGlueStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, config):
    stream = ItGlueStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"page[size]": 1000}
    assert stream.request_params(**inputs) == expected_params


# def test_next_page_token(patch_base_class,config):
#     stream = ItGlueStream(**config)
#     response = MagicMock()
#     response.json.return_value  = {"next-page":{"https://api.itglue.com/expirations?page[size]=1000&page[number]=2"}}
#     inputs = {"response" : response}
#     expected_token = {"page[size]": ["1000"], "page[number]": ["2"]}
#     assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, config):
    stream = ItGlueStream(**config)
    response = MagicMock()
    response.json.return_value = {"people": [{"id": "123", "name": "John Doe"}]}
    inputs = {"response": response, "stream_state": MagicMock()}
    expected_parsed_object = [{"id": "123", "name": "John Doe"}]
    return stream.parse_response(**inputs) == expected_parsed_object


def test_request_headers(patch_base_class, config):
    stream = ItGlueStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"x-api-key": "YXNmnhkjf", "Content-Type": "application/vnd.api+json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class, config):
    stream = ItGlueStream(**config)
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
def test_should_retry(patch_base_class, http_status, should_retry, config):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = ItGlueStream(**config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, config):
    response_mock = MagicMock()
    stream = ItGlueStream(**config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
