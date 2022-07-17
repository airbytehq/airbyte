#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_kyriba.source import KyribaClient, KyribaStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(KyribaStream, "path", "v0/example_endpoint")
    mocker.patch.object(KyribaStream, "primary_key", "test_primary_key")
    mocker.patch.object(KyribaStream, "__abstractmethods__", set())


def config():
    gateway_url = "https://demo.kyriba.com/gateway"
    client = KyribaClient("username", "password", gateway_url)
    client.login = MagicMock(return_value=TokenAuthenticator("token"))
    return {
        "gateway_url": "https://demo.kyriba.com/gateway",
        "client": client,
        "start_date": "2022-01-01",
        "end_date": "2022-03-01",
    }


def test_request_params(patch_base_class):
    stream = KyribaStream(**config())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page.offset": 100}}
    expected_params = {"page.offset": 100}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = KyribaStream(**config())
    # TODO: replace this with your input parameters
    resp = requests.Response()
    resp_dict = {
        "metadata": {
            "links": {"next": "https://next"},
            "pageOffset": 0,
            "pageLimit": 100,
        }
    }
    resp.json = MagicMock(return_value=resp_dict)
    inputs = {"response": resp}
    expected_token = {"page.offset": 100}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = KyribaStream(**config())
    resp = requests.Response()
    resp_dict = {"results": [{"uuid": "uuid"}]}
    resp.json = MagicMock(return_value=resp_dict)
    inputs = {"response": resp}
    expected_parsed_object = {"uuid": "uuid"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = KyribaStream(**config())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = KyribaStream(**config())
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
    stream = KyribaStream(**config())
    assert stream.should_retry(response_mock) == should_retry


def test_should_retry_401(patch_base_class):
    response_mock = MagicMock()
    response_mock.status_code = HTTPStatus.UNAUTHORIZED
    cfg = config()
    client = KyribaClient("username", "password", "https://gateway.url")
    client.login = MagicMock(return_value=TokenAuthenticator("token"))
    client.access_token = "token"
    cfg["client"] = client
    stream = KyribaStream(**cfg)
    client.login.assert_called_once()
    assert stream.should_retry(response_mock)


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = KyribaStream(**config())
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_unnest(patch_base_class):
    stream = KyribaStream(**config())
    data = {"uuid": "uuid", "nested": {"date": "date"}}
    expected = {"uuid": "uuid", "date": "date"}
    assert stream.unnest("nested", data) == expected
