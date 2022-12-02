#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_babelforce.source import BabelforceStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(BabelforceStream, "path", "v0/example_endpoint")
    mocker.patch.object(BabelforceStream, "primary_key", "test_primary_key")
    mocker.patch.object(BabelforceStream, "__abstractmethods__", set())


def test_next_page_token(patch_base_class):
    stream = BabelforceStream(region="services")

    json_response_mock = MagicMock()
    json_response_mock.json.return_value = {"pagination": {"current": 1}}

    inputs = {"response": json_response_mock}
    expected_token = {"page": 2}
    assert stream.next_page_token(**inputs) == expected_token


def test_request_headers(patch_base_class):
    stream = BabelforceStream(region="services")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = BabelforceStream(region="services")
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
    stream = BabelforceStream(region="services")
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = BabelforceStream(region="services")
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
