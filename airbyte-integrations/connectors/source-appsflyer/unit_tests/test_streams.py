#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock
import pytest
import pendulum
from requests.models import Response
from source_appsflyer.source import AppsflyerStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    def __init__(self):
        self.api_token= "secret"
        self.timezone= pendulum.timezone("UTC")
    mocker.patch.object(AppsflyerStream, "__init__", __init__)
    mocker.patch.object(AppsflyerStream, "path", "v0/example_endpoint")
    mocker.patch.object(AppsflyerStream, "primary_key", "test_primary_key")
    mocker.patch.object(AppsflyerStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    timezone = "UTC"
    stream = AppsflyerStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {
        "api_token": "secret",
        "timezone": timezone,
        "maximum_rows": 1_000_000,
        "from": pendulum.yesterday(timezone).to_date_string(),
        "to": pendulum.today(timezone).to_date_string(),
    }
    assert stream.request_params(**inputs) == expected_params


def test_parse_response_return_ok(mocker, patch_base_class):
    mocker.patch.object(AppsflyerStream, "main_fields", ("a", "b"))
    stream = AppsflyerStream()
    response = MagicMock()
    response.iter_lines.return_value = [b"a,b", b"c,d", b"e,f"]
    inputs = {"response": response}
    expected_parsed_object = {"a": "c", "b": "d"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object

def test_parse_response_return_empty_row(mocker, patch_base_class):
    mocker.patch.object(AppsflyerStream, "main_fields", ("a"))
    stream = AppsflyerStream()
    response = MagicMock()
    response.iter_lines.return_value = [b"a"]
    inputs = {"response": response}
    expected_parsed_object = []
    assert list(stream.parse_response(**inputs)) == expected_parsed_object

def test_http_method(patch_base_class):
    stream = AppsflyerStream()
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
    stream = AppsflyerStream()
    assert stream.should_retry(response_mock) == should_retry

def test_should_retry_raw_data(patch_base_class):
    response_mock = MagicMock()
    response_mock.status_code = HTTPStatus.BAD_REQUEST
    response_mock.text = "Your API calls limit has been reached for report type"
    stream = AppsflyerStream()
    assert stream.should_retry(response_mock) == True

def test_should_retry_aggregate_data(patch_base_class):
    response_mock = MagicMock()
    response_mock.status_code = HTTPStatus.FORBIDDEN
    response_mock.text = "Limit reached for "
    stream = AppsflyerStream()
    assert stream.should_retry(response_mock) == True

@pytest.mark.parametrize(
    ("http_status", "expected_backoff_time"),
    [
        (HTTPStatus.OK, None),
        (HTTPStatus.BAD_REQUEST, None),
        (HTTPStatus.TOO_MANY_REQUESTS, None),
        (HTTPStatus.INTERNAL_SERVER_ERROR, None),
    ],
)
def test_backoff_time_default(patch_base_class, http_status, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = AppsflyerStream()
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_backoff_time_aggregate_data(patch_base_class):
    response_mock = MagicMock()
    response_mock.status_code = 403
    response_mock.text = "Limit reached for "
    stream = AppsflyerStream()
    expected_backoff_time = 60
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_backoff_time_raw_data(patch_base_class):
    response_mock = MagicMock()
    response_mock.status_code = 400
    response_mock.text = "Your API calls limit has been reached for report type"
    stream = AppsflyerStream()
    now = pendulum.now("UTC")
    midnight = pendulum.tomorrow("UTC")
    expected_backoff_time = (midnight - now).seconds
    assert stream.backoff_time(response_mock) == expected_backoff_time
