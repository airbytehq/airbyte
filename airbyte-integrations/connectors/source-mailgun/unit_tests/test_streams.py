#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_mailgun.source import Domains, Events, MailgunStream

from . import TEST_CONFIG

DATES_RANGE = {"start_timestamp": 10, "end_timestamp": 20}


@pytest.mark.parametrize(
    "stream,next_page_token,expected",
    [
        (MailgunStream(TEST_CONFIG), None, ""),
        (MailgunStream(TEST_CONFIG), {"url": "next-page-token"}, "next-page-token"),
        (Domains(TEST_CONFIG), None, "domains"),
        (Domains(TEST_CONFIG), {"url": "https://some-url/path/token"}, "https://some-url/path/token"),
        (Events(TEST_CONFIG), None, "events"),
        (Events(TEST_CONFIG), {"url": "https://some-url/path/token"}, "https://some-url/path/token"),
    ],
)
def test_path(stream, next_page_token, expected):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": next_page_token}
    assert stream.path(**inputs) == expected


@pytest.mark.parametrize(
    "stream,stream_slice,stream_state,next_page_token,expected",
    [
        (Domains(TEST_CONFIG), {}, None, None, {}),
        (Events(TEST_CONFIG), {}, {"timestamp": 1609452000.0}, None, {"ascending": "yes", "begin": 1609452000.0}),
        (Events(TEST_CONFIG), {"begin": 10, "end": 20}, {"timestamp": 15}, None, {"begin": 15, "end": 20}),
        (Events(dict(**TEST_CONFIG, **DATES_RANGE)), {"begin": 10, "end": 20}, {}, None, {"begin": 10, "end": 20}),
    ],
)
def test_request_params(stream, stream_slice, stream_state, next_page_token, expected):
    inputs = {"stream_slice": stream_slice, "stream_state": stream_state, "next_page_token": next_page_token}
    assert stream.request_params(**inputs) == expected


@pytest.mark.parametrize(
    "stream",
    [
        MailgunStream(TEST_CONFIG),
        Domains(TEST_CONFIG),
        Events(TEST_CONFIG),
    ],
)
class TestStreams:
    def test_next_page_token(self, stream, normal_response, next_page_url):
        inputs = {"response": normal_response}
        assert stream.next_page_token(**inputs) == {"url": next_page_url}

    def test_next_page_token_last_page(self, stream):
        response = MagicMock()
        response.json = MagicMock(return_value={"items": [], "paging": {"next": "some-url"}})
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


@pytest.mark.parametrize(
    "stream_class",
    [
        MailgunStream,
        Domains,
        Events,
    ],
)
def test_domain_region(stream_class, test_config):
    assert stream_class(config=test_config).url_base == "https://api.mailgun.net/v3/"

    test_config["domain_region"] = "EU"
    assert stream_class(config=test_config).url_base == "https://api.eu.mailgun.net/v3/"

    test_config["domain_region"] = "US"
    assert stream_class(config=test_config).url_base == "https://api.mailgun.net/v3/"
