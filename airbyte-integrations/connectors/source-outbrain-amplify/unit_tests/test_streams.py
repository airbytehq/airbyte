#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import inspect
import json
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_outbrain_amplify.source import OutbrainAmplifyStream


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(OutbrainAmplifyStream, "path", "v0/example_endpoint")
    mocker.patch.object(OutbrainAmplifyStream, "primary_key", "test_primary_key")
    mocker.patch.object(OutbrainAmplifyStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = OutbrainAmplifyStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = OutbrainAmplifyStream()
    inputs = {"totalCount": 100, "count": 50}
    pagination_token = json.dumps(inputs)
    response = requests.Response()
    response.status_code = 200
    response.headers["content-type"] = "application/json"
    response._content = pagination_token.encode("utf-8")
    expected_token = {"offset": 51}
    assert stream.next_page_token(response) == expected_token


def test_parse_response(patch_base_class):
    stream = OutbrainAmplifyStream()
    mock_response = {"campaigns": [], "totalCount": 5, "count": 0}
    mock_response = json.dumps(mock_response)
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response._content = mock_response.encode("utf-8")
    result = stream.parse_response(response)
    expected_result = True
    assert inspect.isgenerator(result) == expected_result


def test_request_headers(patch_base_class):
    stream = OutbrainAmplifyStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = OutbrainAmplifyStream()
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
    stream = OutbrainAmplifyStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = OutbrainAmplifyStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_get_time_interval(patch_base_class):
    stream = OutbrainAmplifyStream()
    start_date = "2022-08-03 00:00:00"
    ending_date = "2022-08-02 00:00:00"
    try:
        stream._get_time_interval(start_date, ending_date)
    except ValueError as e:
        assert e
