#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from pytest import fixture
from requests import Response
from source_microsoft_dataverse.source import IncrementalMicrosoftDataverseStream, MicrosoftDataverseStream

from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


@fixture
def incremental_config():
    return {
        "url": "http://test-url",
        "stream_name": "test_stream",
        "stream_path": "test_path",
        "primary_key": [["test_primary_key"]],
        "schema": {},
        "odata_maxpagesize": 100,
        "authenticator": MagicMock(),
    }


@pytest.mark.parametrize(
    ("inputs", "expected_params"),
    [
        ({"stream_slice": None, "stream_state": {}, "next_page_token": None}, {}),
        ({"stream_slice": None, "stream_state": {}, "next_page_token": {"$skiptoken": "skiptoken"}}, {"$skiptoken": "skiptoken"}),
        ({"stream_slice": None, "stream_state": {"$deltatoken": "delta"}, "next_page_token": None}, {}),
    ],
)
def test_request_params(inputs, expected_params, incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    assert stream.request_params(**inputs) == expected_params


def test_stream_resumability(incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    assert stream.is_resumable is False
    assert stream.get_cursor() is None

    incremental_stream = IncrementalMicrosoftDataverseStream(**incremental_config, config_cursor_field=["test_cursor_field"])
    assert incremental_stream.is_resumable is True


@pytest.mark.parametrize(
    ("response_json", "next_page_token"),
    [
        (
            {
                "@odata.nextLink": "https://url?$skiptoken=oEBwdSP6uehIAxQOWq_3Ksh_TLol6KIm3stvdc6hGhZRi1hQ7Spe__dpvm3U4zReE4CYXC2zOtaKdi7KHlUtC2CbRiBIUwOxPKLa"
            },
            {"$skiptoken": "oEBwdSP6uehIAxQOWq_3Ksh_TLol6KIm3stvdc6hGhZRi1hQ7Spe__dpvm3U4zReE4CYXC2zOtaKdi7KHlUtC2CbRiBIUwOxPKLa"},
        ),
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
    response.json.return_value = {"value": [{"test-key": "test-value"}]}
    inputs = {"response": response}
    expected_parsed_object = {"test-key": "test-value"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {
        "Cache-Control": "no-cache",
        "OData-Version": "4.0",
        "Content-Type": "application/json",
        "Prefer": "odata.maxpagesize=100",
    }
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(incremental_config):
    stream = MicrosoftDataverseStream(**incremental_config)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "expected_action"),
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
    ],
)
def test_error_handler(incremental_config, http_status, expected_action):
    response_mock = Response()
    response_mock.status_code = http_status
    stream = MicrosoftDataverseStream(**incremental_config)
    error_handler = stream.get_error_handler() or stream._http_client._error_handler
    assert error_handler.interpret_response(response_mock).response_action == expected_action
