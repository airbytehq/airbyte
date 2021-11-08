#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_linnworks.streams import LinnworksStream


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(LinnworksStream, "path", "v0/example_endpoint")
    mocker.patch.object(LinnworksStream, "primary_key", "test_primary_key")
    mocker.patch.object(LinnworksStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = LinnworksStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = LinnworksStream()
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, requests_mock):
    stream = LinnworksStream()
    requests_mock.get(
        "https://dummy",
        json={
            "Foo": "foo",
            "Bar": {
                "Baz": "baz",
            },
        },
    )
    resp = requests.get("https://dummy")
    inputs = {"response": resp}
    expected_parsed_object = {"Bar": {"Baz": "baz"}, "Foo": "foo"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = LinnworksStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = LinnworksStream()
    expected_method = "POST"
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
    stream = LinnworksStream()
    assert stream.should_retry(response_mock) == should_retry


@pytest.mark.parametrize(
    ("header_name", "header_value", "expected"),
    [
        ("Retry-After", "123", 123),
        ("Retry-After", "-123", -123),
    ],
)
def test_backoff_time(patch_base_class, requests_mock, header_name, header_value, expected):
    stream = LinnworksStream()
    requests_mock.get("https://dummy", headers={header_name: header_value}, status_code=429)
    result = stream.backoff_time(requests.get("https://dummy"))
    assert result == expected
