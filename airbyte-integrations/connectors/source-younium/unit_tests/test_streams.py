#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_younium.source import YouniumStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(YouniumStream, "path", "v0/example_endpoint")
    mocker.patch.object(YouniumStream, "primary_key", "test_primary_key")
    mocker.patch.object(YouniumStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = YouniumStream(authenticator=None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"PageSize": 100}
    assert stream.request_params(**inputs) == expected_params


def test_request_params_with_next_page_token(patch_base_class):
    stream = YouniumStream(authenticator=None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"pageNumber": 2}}
    expected_params = {"PageSize": 100, "pageNumber": 2}
    assert stream.request_params(**inputs) == expected_params


def test_playground_url_base(patch_base_class):
    stream = YouniumStream(authenticator=None, playground=True)
    expected_url_base = "https://apisandbox.younium.com"
    assert stream.url_base == expected_url_base


def test_use_playground_url_base(patch_base_class):
    stream = YouniumStream(authenticator=None, playground=True)
    expected_url_base = "https://apisandbox.younium.com"
    assert stream.url_base == expected_url_base


def test_http_method(patch_base_class):
    stream = YouniumStream(authenticator=None)
    # TODO: replace this with your expected http request method
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
    stream = YouniumStream(authenticator=None)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = YouniumStream(authenticator=None)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
