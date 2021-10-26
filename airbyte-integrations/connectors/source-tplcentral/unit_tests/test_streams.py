#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_tplcentral.streams import TplcentralStream


@pytest.fixture
def config():
    return {
        "config": {
            "authenticator": None,
            "url_base": "https://secure-wms.com/",
            "client_id": "xxx",
            "client_secret": "yyy",
            "user_login_id": 123,
            "tpl_key": "{00000000-0000-0000-0000-000000000000}",
            "customer_id": 4,
            "facility_id": 5,
            "start_date": "2021-10-01"
        }
    }


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(TplcentralStream, "path", "v0/example_endpoint")
    mocker.patch.object(TplcentralStream, "primary_key", "test_primary_key")
    mocker.patch.object(TplcentralStream, "cursor_field", "test_cursor_field")
    mocker.patch.object(TplcentralStream, "collection_field", "CollectionField")
    mocker.patch.object(TplcentralStream, "__abstractmethods__", set())


@pytest.fixture
def patch_base_class_page_size(mocker):
    mocker.patch.object(TplcentralStream, "page_size", 10)


@pytest.fixture
def patch_base_class_upstream_primary_key(mocker):
    mocker.patch.object(TplcentralStream, "upstream_primary_key", "Nested.PrimaryKey")


@pytest.fixture
def patch_base_class_upstream_cursor_field(mocker):
    mocker.patch.object(TplcentralStream, "upstream_cursor_field", "Nested.Cursor")


@pytest.fixture
def stream(patch_base_class, config):
    return TplcentralStream(**config)


def test_request_params(stream):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": "next_page_token_is_the_params"}
    expected_params = "next_page_token_is_the_params"

    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(stream, requests_mock):
    # No results
    requests_mock.get("https://dummy", json={"TotalResults": 0, "CollectionField": []})
    resp = requests.get("https://dummy")
    expected_next_page_token = None
    assert stream.next_page_token(resp) == expected_next_page_token

    # Invalid response
    requests_mock.get("https://dummy", json={"TotalResults": 1000, "CollectionField": []})
    resp = requests.get("https://dummy")
    expected_next_page_token = None
    assert stream.next_page_token(resp) == expected_next_page_token

    # Implicit page size
    requests_mock.get("https://dummy", json={"TotalResults": 1000, "CollectionField": [None, None, None]})
    resp = requests.get("https://dummy")
    expected_next_page_token = {"pgsiz": 3, "pgnum": 2}
    assert stream.next_page_token(resp) == expected_next_page_token


def test_next_page_token_with_page_size(patch_base_class_page_size, stream, requests_mock):
    # Explicit page size
    requests_mock.get("https://dummy", json={"TotalResults": 1000, "CollectionField": []})
    resp = requests.get("https://dummy")
    expected_next_page_token = {"pgsiz": 10, "pgnum": 2}
    assert stream.next_page_token(resp) == expected_next_page_token


def test_parse_response(stream, requests_mock):
    requests_mock.get("https://dummy", json={
        "TotalResults": 2,
        "CollectionField": [
            {
                "Foo": "foo",
                "Bar": {
                    "Baz": "baz",
                },
                "_links": [],
            }
        ]
    })
    resp = requests.get("https://dummy")
    inputs = {"response": resp}
    expected_parsed_object = {"bar": {"baz": "baz"}, "foo": "foo"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_with_primary_key(patch_base_class_upstream_primary_key, stream, requests_mock):
    requests_mock.get("https://dummy", json={
        "TotalResults": 2,
        "CollectionField": [
            {
                "Nested": {
                    "PrimaryKey": 42,
                },
            },
        ]
    })
    resp = requests.get("https://dummy")
    inputs = {"response": resp}
    expected_parsed_object = {"nested": {"primary_key": 42}, "test_primary_key": 42}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_with_cursor_field(patch_base_class_upstream_cursor_field, stream, requests_mock):
    requests_mock.get("https://dummy", json={
        "TotalResults": 2,
        "CollectionField": [
            {
                "Nested": {
                    "Cursor": 43,
                },
            },
        ]
    })
    resp = requests.get("https://dummy")
    inputs = {"response": resp}
    expected_parsed_object = {"nested": {"cursor": 43}, "test_cursor_field": 43}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(stream):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(stream):
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
def test_should_retry(stream, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(stream):
    response_mock = MagicMock()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
