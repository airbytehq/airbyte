#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_timely.source import TimelyIntegrationStream


@pytest.fixture()
def config(request):
    args = {"account_id": "123", "start_date": "2022-04-01", "bearer_token": "51UWRAsFuIbeygfIY3XfucQUGiX"}
    return args


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(TimelyIntegrationStream, "path", "v0/example_endpoint")
    mocker.patch.object(TimelyIntegrationStream, "primary_key", "test_primary_key")
    mocker.patch.object(TimelyIntegrationStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, config):
    stream = TimelyIntegrationStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"account_id": "123", "page": 1, "per_page": "1000"}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, config):
    stream = TimelyIntegrationStream(**config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_request_headers(patch_base_class, config):
    stream = TimelyIntegrationStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Authorization": "Bearer 51UWRAsFuIbeygfIY3XfucQUGiX", "Content-Type": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class, config):
    stream = TimelyIntegrationStream(**config)
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
    stream = TimelyIntegrationStream(**config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, config):
    response_mock = MagicMock()
    stream = TimelyIntegrationStream(**config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
