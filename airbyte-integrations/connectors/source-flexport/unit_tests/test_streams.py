#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from requests.exceptions import HTTPError
from source_flexport.source import FlexportError
from source_flexport.streams import FlexportStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(FlexportStream, "path", "v0/example_endpoint")
    mocker.patch.object(FlexportStream, "primary_key", "test_primary_key")
    mocker.patch.object(FlexportStream, "__abstractmethods__", set())


@pytest.mark.parametrize(
    ("next_page_token", "expected"),
    [
        (None, {"page": 1, "per": FlexportStream.page_size}),
        ({"page": 2, "per": 50}, {"page": 2, "per": 50}),
    ],
)
def test_request_params(patch_base_class, next_page_token, expected):
    stream = FlexportStream()
    assert stream.request_params(next_page_token=next_page_token) == expected


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ({"data": {"next": None}}, None),
        ({"data": {"next": "/endpoint"}}, KeyError("page")),
        ({"data": {"next": "/endpoint?page=2"}}, KeyError("per")),
        ({"data": {"next": "/endpoint?page=2&per=42"}}, {"page": "2", "per": "42"}),
    ],
)
def test_next_page_token(patch_base_class, requests_mock, response, expected):
    url = "http://dummy"
    requests_mock.get(url, json=response)
    response = requests.get(url)

    stream = FlexportStream()

    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=str(expected)):
            stream.next_page_token(response)
    else:
        assert stream.next_page_token(response) == expected


@pytest.mark.parametrize(
    ("status_code", "response", "expected"),
    [
        (200, None, Exception()),
        (400, None, Exception()),
        (200, "string_response", FlexportError("Unexpected response")),
        (401, "string_response", FlexportError("Unexpected response")),
        (200, {"error": None}, KeyError("data")),
        (402, {"error": None}, HTTPError("402 Client Error")),
        (200, {"error": {}}, KeyError("data")),
        (403, {"error": {}}, HTTPError("403 Client Error")),
        (200, {"error": "unexpected_error_type"}, FlexportError("Unexpected error: unexpected_error_type")),
        (404, {"error": "unexpected_error_type"}, FlexportError("Unexpected error: unexpected_error_type")),
        (200, {"error": {"code": "error_code", "message": "Error message"}}, FlexportError("error_code: Error message")),
        (405, {"error": {"code": "error_code", "message": "Error message"}}, FlexportError("error_code: Error message")),
        (200, {"error": None, "data": "unexpected_data_type"}, TypeError("string indices must be integers")),
        (200, {"error": None, "data": {"data": None}}, TypeError("'NoneType' object is not iterable")),
        (200, {"error": None, "data": {"data": "hello"}}, ["h", "e", "l", "l", "o"]),
        (200, {"error": None, "data": {"data": ["record_1", "record_2"]}}, ["record_1", "record_2"]),
    ],
)
def test_parse_response(patch_base_class, requests_mock, status_code, response, expected):
    url = "http://dummy"
    requests_mock.get(url, status_code=status_code, json=response)
    response = requests.get(url)

    stream = FlexportStream()

    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=str(expected)):
            list(stream.parse_response(response))
    else:
        assert list(stream.parse_response(response)) == expected
