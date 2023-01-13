#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_genesys.source import GenesysStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GenesysStream, "path", "v0/example_endpoint")
    mocker.patch.object(GenesysStream, "primary_key", "test_primary_key")
    mocker.patch.object(GenesysStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = GenesysStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"pageSize": 500}
    assert stream.request_params(**inputs) == expected_params


def test_request_headers(patch_base_class):
    stream = GenesysStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert len(stream.request_headers(**inputs)) == 0


def test_http_method(patch_base_class):
    stream = GenesysStream()
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
    stream = GenesysStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = GenesysStream()
    expected_backoff_time = 1
    assert stream.backoff_time(response_mock) == expected_backoff_time
