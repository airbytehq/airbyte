#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_appfollow.source import AppfollowStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    def __init__(self):
        self.ext_id = "00000"
        self.cid = "000000"

    mocker.patch.object(AppfollowStream, "__init__", __init__)
    mocker.patch.object(AppfollowStream, "path", "v0/example_endpoint")
    mocker.patch.object(AppfollowStream, "primary_key", "test_primary_key")
    mocker.patch.object(AppfollowStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = AppfollowStream()
    inputs = {"stream_state": "test_stream_state"}
    expected_params = {"ext_id": "00000", "cid": "000000"}
    assert stream.request_params(**inputs) == expected_params


def test_parse_response(patch_base_class):
    stream = AppfollowStream()
    mock_response = MagicMock()
    inputs = {"stream_state": "test_stream_state", "response": mock_response}
    expected_parsed_object = mock_response.json()
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = AppfollowStream()
    inputs = {"stream_state": "test_stream_state"}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = AppfollowStream()
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
    stream = AppfollowStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = AppfollowStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
