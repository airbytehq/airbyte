#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from source_insightly.source import InsightlyStream

authenticator = BasicHttpAuthenticator(username="test", password="")


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(InsightlyStream, "path", "v0/example_endpoint")
    mocker.patch.object(InsightlyStream, "primary_key", "test_primary_key")
    mocker.patch.object(InsightlyStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"count_total": True, "skip": 0, "top": 500}
    assert stream.request_params(**inputs) == expected_params


def test_request_param_with_next_page_token(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": 1000}
    expected_params = {"count_total": True, "skip": 1000, "top": 500}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
    stream.total_count = 10000

    request = MagicMock()
    request.url = "https://api.insight.ly/v0/example_endpoint?count_total=True&skip=0&top=500"
    response = MagicMock()
    response.status_code = HTTPStatus.OK
    response.request = request

    inputs = {"response": response}
    expected_token = 500
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_last_records(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
    stream.total_count = 2100

    request = MagicMock()
    request.url = "https://api.insight.ly/v0/example_endpoint?count_total=True&skip=1500&top=500"
    response = MagicMock()
    response.status_code = HTTPStatus.OK
    response.request = request

    inputs = {"response": response}
    expected_token = 2000
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_no_more_records(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
    stream.total_count = 1000

    request = MagicMock()
    request.url = "https://api.insight.ly/v0/example_endpoint?count_total=True&skip=1000&top=500"
    response = MagicMock()
    response.status_code = HTTPStatus.OK
    response.request = request

    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)

    response = MagicMock()
    response.json = MagicMock(return_value=[{"data_field": [{"keys": ["keys"]}]}])

    inputs = {"stream_state": "test_stream_state", "response": response}
    expected_parsed_object = response.json()[0]
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Accept": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = InsightlyStream(authenticator=authenticator)
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
    stream = InsightlyStream(authenticator=authenticator)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = InsightlyStream(authenticator=authenticator)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
