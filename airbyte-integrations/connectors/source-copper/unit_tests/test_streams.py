#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_copper.source import CopperStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CopperStream, "path", "v0/example_endpoint")
    mocker.patch.object(CopperStream, "primary_key", "test_primary_key")
    mocker.patch.object(CopperStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = CopperStream()
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request parameters
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_request_headers(patch_base_class):
    stream = CopperStream()
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request headers
    expected_headers = {
        "Content-type": "application/json",
        "X-PW-AccessToken": None,
        "X-PW-Application": "developer_api",
        "X-PW-UserEmail": None,
    }
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = CopperStream()
    # TODO: replace this with your expected http request method
    expected_method = "POST"
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
    stream = CopperStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = CopperStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
