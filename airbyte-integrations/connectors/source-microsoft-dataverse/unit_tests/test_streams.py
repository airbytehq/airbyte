#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from pytest import fixture
from source_microsoft_dataverse.source import MicrosoftDataverseStream


@fixture
def incremental_config():
    return {
        "url": "http://test-url",
        "stream_name": "test_stream",
        "stream_path": "test_path",
        "primary_key": [["test_primary_key"]],
        "schema": {

        },
        "odata_maxpagesize": 100,
        "authenticator": MagicMock()
    }


@pytest.mark.parametrize(
    ("inputs", "expected_params"),
    [
        ({"stream_slice": None, "stream_state": {}, "next_page_token": None}, {}),
        ({"stream_slice": None, "stream_state": {}, "next_page_token": {"$skiptoken": "skiptoken"}}, {"$skiptoken": "skiptoken"}),
        ({"stream_slice": None, "stream_state": {"$deltatoken": "delta"}, "next_page_token": None}, {"$deltatoken": "delta"})
    ],
)
def test_request_params(inputs, expected_params, incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    ("response_json", "next_page_token"),
    [
        ({"@odata.nextLink": "https://url?$skiptoken=oEBwdSP6uehIAxQOWq_3Ksh_TLol6KIm3stvdc6hGhZRi1hQ7Spe__dpvm3U4zReE4CYXC2zOtaKdi7KHlUtC2CbRiBIUwOxPKLa"},
         {"$skiptoken": "oEBwdSP6uehIAxQOWq_3Ksh_TLol6KIm3stvdc6hGhZRi1hQ7Spe__dpvm3U4zReE4CYXC2zOtaKdi7KHlUtC2CbRiBIUwOxPKLa"}),
        ({"value": []}, None),
    ],
)
def test_next_page_token(response_json, next_page_token, incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    response = MagicMock()
    response.json.return_value = response_json
    inputs = {"response": response}
    expected_token = next_page_token
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    response = MagicMock()
    response.json.return_value = {
        "value": [
            {
                "test-key": "test-value"
            }
        ]
    }
    inputs = {"response": response}
    expected_parsed_object = {
        "test-key": "test-value"
    }
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {
        "Cache-Control": "no-cache",
        "OData-Version": "4.0",
        "Content-Type": "application/json",
        "Prefer": "odata.maxpagesize=100"
    }
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
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
def test_should_retry(incremental_config, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = MicrosoftDataverseStream(**incremental_config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(incremental_config):
    response_mock = MagicMock()
    stream = MicrosoftDataverseStream(**incremental_config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
