#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_genesys.source import GenesysStream

from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GenesysStream, "path", "v0/example_endpoint")
    mocker.patch.object(GenesysStream, "primary_key", "test_primary_key")
    mocker.patch.object(GenesysStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = GenesysStream(api_base_url="https://dummy.url")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"pageSize": 500}
    assert stream.request_params(**inputs) == expected_params


def test_request_headers(patch_base_class):
    stream = GenesysStream(api_base_url="https://dummy.url")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert len(stream.request_headers(**inputs)) == 0


def test_http_method(patch_base_class):
    stream = GenesysStream(api_base_url="https://dummy.url")
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "response_action"),
    [
        (HTTPStatus.OK, ResponseAction.SUCCESS),
        (HTTPStatus.BAD_REQUEST, ResponseAction.FAIL),
        (HTTPStatus.TOO_MANY_REQUESTS, ResponseAction.RATE_LIMITED),
        (HTTPStatus.INTERNAL_SERVER_ERROR, ResponseAction.RETRY),
    ],
)
def test_error_handler_response_action(patch_base_class, http_status, response_action):
    response = requests.Response()
    response.status_code = http_status
    stream = GenesysStream(api_base_url="https://dummy.url")
    assert stream._http_client._error_handler.interpret_response(response).response_action == response_action


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = GenesysStream(api_base_url="https://dummy.url")
    expected_backoff_time = 1
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_backoff_time_uses_retry_after_header(patch_base_class):
    response = requests.Response()
    response.headers["Retry-After"] = "7"
    stream = GenesysStream(api_base_url="https://dummy.url")
    assert stream.get_backoff_strategy().backoff_time(response, attempt_count=1) == 7


def test_url_base(patch_base_class):
    api_base_url = "https://dummy.url"
    stream = GenesysStream(api_base_url=api_base_url)
    assert stream.url_base == api_base_url + "/api/v2/"
