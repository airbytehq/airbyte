#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_mailgun.source import Domains, Events, MailgunStream

from . import TEST_CONFIG


@pytest.mark.parametrize(
    "stream,stream_slice,stream_state,next_page_token,expected",
    [
        (MailgunStream(), None, None, None, ""),
        (MailgunStream(), None, None, {"url": "next-page-token"}, "next-page-token"),

        (Domains(), None, None, None, "domains"),
        (Domains(), None, None, {"url": "https://some-url/path/token"}, "domains/token"),

        (Events(TEST_CONFIG), None, None, None, "events"),
        (Events(TEST_CONFIG), None, None, {"url": "https://some-url/path/token"}, "events/token"),
    ]
)
def test_path(stream, stream_slice, stream_state, next_page_token, expected):
    inputs = {"stream_slice": stream_slice, "stream_state": stream_state, "next_page_token": next_page_token}
    assert stream.path(**inputs) == expected


@pytest.mark.parametrize(
    "stream,stream_slice,stream_state,next_page_token,expected",
    [
        (Domains(), None, None, None, {}),
        (Events(TEST_CONFIG), None, {"begin": 1609452000.0}, None, {"ascending": "yes", "begin": 1609452000.0}),
    ]
)
def test_request_params(stream, stream_slice, stream_state, next_page_token, expected):
    inputs = {"stream_slice": stream_slice, "stream_state": stream_state, "next_page_token": next_page_token}
    assert stream.request_params(**inputs) == expected


@pytest.mark.parametrize(
    "stream",
    [
        MailgunStream(), Domains(), Events(TEST_CONFIG),
    ]
)
class TestStreams:

    def test_next_page_token(self, stream, normal_response, next_page_url):
        inputs = {"response": normal_response}
        assert stream.next_page_token(**inputs) == {"url": next_page_url}

    def test_next_page_token_last_page(self, stream):
        response = MagicMock()
        response.json = MagicMock(return_value={
            "items": [],
            "paging": {
                "next": "some-url"
            }
        })
        inputs = {"response": response}
        assert stream.next_page_token(**inputs) is None

    def test_parse_response(self, stream, normal_response, test_records):
        inputs = {"response": normal_response}
        expected_parsed_object = test_records[0]
        assert next(stream.parse_response(**inputs)) == expected_parsed_object

    def test_request_headers(self, stream):
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_headers = {}
        assert stream.request_headers(**inputs) == expected_headers

    def test_http_method(self, stream):
        expected_method = "GET"
        assert stream.http_method == expected_method

    def test_backoff_time(self, stream):
        response_mock = MagicMock()
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    @pytest.mark.parametrize(
        ("http_status", "should_retry"),
        [
            (HTTPStatus.OK, False),
            (HTTPStatus.BAD_REQUEST, False),
            (HTTPStatus.TOO_MANY_REQUESTS, True),
            (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        ],
    )
    def test_should_retry(self, stream, http_status, should_retry):
        response_mock = MagicMock()
        response_mock.status_code = http_status
        assert stream.should_retry(response_mock) == should_retry
