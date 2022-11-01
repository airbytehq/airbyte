#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus

# from unittest import result
from unittest.mock import MagicMock

import pytest
from source_zenefits.source import ZenefitsStream


@pytest.fixture()
def config(request):
    args = {"token": "YXNmnhkjf"}
    return args


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ZenefitsStream, "path", "v0/example_endpoint")
    mocker.patch.object(ZenefitsStream, "primary_key", "test_primary_key")
    mocker.patch.object(ZenefitsStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, config):
    stream = ZenefitsStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"limit": 100}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, config):
    stream = ZenefitsStream(**config)
    response = MagicMock()
    response.json.return_value = {"data": {"next_url": "https://api.zenefits.com/core/people?limit=100&starting_after=22334422"}}
    inputs = {"response": response}
    expected_token = {"limit": ["100"], "starting_after": ["22334422"]}
    assert stream.next_page_token(**inputs) == expected_token


def test_request_headers(patch_base_class, config):
    stream = ZenefitsStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Authorization": "Bearer YXNmnhkjf", "Content-Type": "application/json", "Accept": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_parse_response(patch_base_class, config):
    stream = ZenefitsStream(**config)
    response = MagicMock()
    response.json.return_value = {"people": [{"id": "123", "name": "John Doe"}]}
    inputs = {"response": response, "stream_state": MagicMock()}
    expected_parsed_object = [{"id": "123", "name": "John Doe"}]
    return stream.parse_response(**inputs) == expected_parsed_object


def test_http_method(patch_base_class, config):
    stream = ZenefitsStream(**config)
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
    stream = ZenefitsStream(**config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, config):
    response_mock = MagicMock()
    stream = ZenefitsStream(**config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
