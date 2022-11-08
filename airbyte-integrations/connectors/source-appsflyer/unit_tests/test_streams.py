#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pendulum
import pytest
from source_appsflyer.source import AppsflyerStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    def __init__(self):
        self.api_token = "secret"
        self.timezone = pendulum.timezone("UTC")

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


@pytest.mark.parametrize(
    ("main_fields", "return_value", "expected_parsed_object"),
    [
        (("a", "b"), [b"a,b", b"c,d"], [{"a": "c", "b": "d"}]),
        (("a"), [b"a"], []),
    ],
)
def test_parse_response(patch_base_class, mocker, main_fields, return_value, expected_parsed_object):
    mocker.patch.object(AppsflyerStream, "main_fields", main_fields)
    stream = AppsflyerStream()
    response = MagicMock()
    response.iter_lines.return_value = return_value
    inputs = {"response": response}
    assert list(stream.parse_response(**inputs)) == expected_parsed_object


def test_http_method(patch_base_class):
    stream = AppsflyerStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "response_text", "should_retry"),
    [
        (HTTPStatus.OK, "", False),
        (HTTPStatus.BAD_REQUEST, "", False),
        (HTTPStatus.TOO_MANY_REQUESTS, "", True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, "", True),
        (HTTPStatus.BAD_REQUEST, "Your API calls limit has been reached for report type", True),
        (HTTPStatus.FORBIDDEN, "Limit reached for ", True),
    ],
)
def test_should_retry(patch_base_class, http_status, response_text, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    response_mock.text = response_text
    stream = AppsflyerStream()
    assert stream.should_retry(response_mock) == should_retry


@pytest.mark.parametrize(
    ("http_status", "response_text", "expected_backoff_time"),
    [
        (HTTPStatus.OK, "", None),
        (HTTPStatus.BAD_REQUEST, "", None),
        (HTTPStatus.TOO_MANY_REQUESTS, "", None),
        (HTTPStatus.INTERNAL_SERVER_ERROR, "", None),
        (HTTPStatus.FORBIDDEN, "Limit reached for ", 60),  # Wait time for aggregate data is 60 Seconds.
        (
            HTTPStatus.BAD_REQUEST,
            "Your API calls limit has been reached for report type",
            "Midnight",
        ),  # Wait time for raw data is Midnight UTC - Now UTC.
    ],
)
def test_backoff_time(patch_base_class, http_status, response_text, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    response_mock.text = response_text
    stream = AppsflyerStream()
    if expected_backoff_time == "Midnight":
        expected_backoff_time = (pendulum.tomorrow("UTC") - pendulum.now("UTC")).seconds
    assert stream.backoff_time(response_mock) == expected_backoff_time
