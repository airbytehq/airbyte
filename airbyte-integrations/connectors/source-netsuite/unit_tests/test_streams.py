#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch
import requests_mock

import pytest
from multiprocessing.pool import Pool
from source_netsuite.source import NetsuiteStream, SourceNetsuite
from requests_oauthlib import OAuth1

config = {
    "consumer_key": "consumer_key",
    "consumer_secret": "consumer_secret",
    "token_id": "token_id",
    "token_secret": "token_secret",
    "realm": "12345",
}


def make_stream():
    src = SourceNetsuite()
    auth = src.auth(config)
    url = src.record_url(config)
    return NetsuiteStream(auth, "invoice", url)


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(NetsuiteStream, "path", "v0/example_endpoint")
    mocker.patch.object(NetsuiteStream, "primary_key", "test_primary_key")
    mocker.patch.object(NetsuiteStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = make_stream()
    stream.start_datetime = "2022-01-01T00:00:00Z"
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 1000}}
    expected_params = {"offset": 1000, "q": "lastModifiedDate AFTER 2022-01-01 12:00:00 AM"}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = make_stream()
    response = MagicMock()
    response.json = MagicMock(return_value={"hasMore": True, "offset": 0, "count": 1000})
    inputs = {"response": response}
    expected_token = {"offset": 1000}
    assert stream.next_page_token(**inputs) == expected_token


def test_format_date(patch_base_class):
    stream = make_stream()
    inpt = "2022-01-01T00:00:00Z"
    expected = "2022-01-01 12:00:00 AM"
    assert stream.format_date(inpt) == expected


def test_fetch_record(patch_base_class, requests_mock):
    stream = make_stream()
    expected = {"id": 1}
    record = {"links": [{"href": "https://netsuite.com/1"}]}
    requests_mock.get("https://netsuite.com/1", json={"id": 1})
    assert expected == stream.fetch_record(record, {})


def test_parse_response(patch_base_class):
    stream = make_stream()
    response = MagicMock()
    response.json = MagicMock(return_value={"items": [{"id": 1}]})
    inputs = {"response": response, "stream_state": {}}
    expected_parsed_object = {"id": 1}
    with patch.object(Pool, "starmap", return_value=[{"id": 1}]):
        assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_http_method(patch_base_class):
    stream = make_stream()
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
    stream = make_stream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = make_stream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
