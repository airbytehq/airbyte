#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest


def test_request_params(stream):
    start_date = "2022-07-07"
    end_date = "2022-08-07"
    inputs = {
        "stream_slice": {"start_date": start_date, "end_date": end_date},
        "stream_state": None,
        "next_page_token": None,
    }
    expected_params = {"sort": "asc", "limit": 10}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(stream):
    expected_token = {"next_url": "url_to_next_page"}
    assert (
            stream.next_page_token(
                response=MagicMock(json=lambda: expected_token),
            )
            == expected_token
    )


def test_parse_response(stream):
    body = {"resultsCount": 1, "results": [{"t": 1000000, "c": 200, }], }
    inputs = {
        "response": MagicMock(json=lambda: body),
        "stream_state": {},
    }
    result = [{'date': '1970-01-01', 'price': 200, 'stock_ticker': 'TSLA'}]
    assert stream.parse_response(**inputs) == result


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
