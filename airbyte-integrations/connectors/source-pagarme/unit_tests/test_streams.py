#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_pagarme.streams import PagarmeStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PagarmeStream, "path", "v0/example_endpoint")
    mocker.patch.object(PagarmeStream, "primary_key", "test_primary_key")
    mocker.patch.object(PagarmeStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = PagarmeStream(api_key="key")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {'count': 1000}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = PagarmeStream(api_key="key")
    inputs = {"response": MagicMock()}
    expected_token = 2
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = PagarmeStream(api_key="key")
    response = MagicMock()
    response.json.return_value = [{"id": 71625167165}]
    inputs = {"response": response, "stream_state": None}
    expected_parsed_object = {"id": 71625167165}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = PagarmeStream(api_key="key")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = PagarmeStream(api_key="key")
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
    stream = PagarmeStream(api_key="key")
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = PagarmeStream(api_key="key")
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
