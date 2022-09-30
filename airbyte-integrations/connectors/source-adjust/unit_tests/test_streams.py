#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_adjust.source import AdjustReportStream


@pytest.fixture
def stream():
    return AdjustReportStream(
        connector=None,
        config={
            "ingest_start": "2022-07-01",
            "dimensions": [],
            "metrics": [],
            "additional_metrics": [],
            "api_token": "",
        },
    )


def test_request_params(stream):
    some_date = "2022-07-07"
    inputs = {
        "stream_slice": {"day": some_date},
        "stream_state": None,
        "next_page_token": None,
    }
    expected_params = {
        "date_period": f"{some_date}:{some_date}",
        "dimensions": "day",
        "metrics": "",
    }
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(stream):
    expected_token = None
    assert (
        stream.next_page_token(
            response=None,
        )
        == expected_token
    )


def test_parse_response(stream):
    body = {
        "rows": [
            {
                "device_type": "phone",
                "app_token": "some id",
            }
        ],
    }
    inputs = {
        "response": MagicMock(json=lambda: body),
        "stream_state": {},
    }
    assert next(stream.parse_response(**inputs)) == body["rows"][0]


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
