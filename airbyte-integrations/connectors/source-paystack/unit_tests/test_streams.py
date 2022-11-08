#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_paystack.streams import PaystackStream

START_DATE = "2020-08-01T00:00:00Z"


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PaystackStream, "path", "v0/example_endpoint")
    mocker.patch.object(PaystackStream, "primary_key", "test_primary_key")
    mocker.patch.object(PaystackStream, "__abstractmethods__", set())


def test_request_params_includes_pagination_limit(patch_base_class):
    stream = PaystackStream(start_date=START_DATE)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}

    params = stream.request_params(**inputs)

    assert params == {"perPage": 200}


def test_request_params_for_includes_page_number_for_pagination(patch_base_class):
    stream = PaystackStream(start_date=START_DATE)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 2}}

    params = stream.request_params(**inputs)

    assert params == {"perPage": 200, "page": 2}


def test_next_page_token_increments_page_number(patch_base_class):
    stream = PaystackStream(start_date=START_DATE)
    mock_response = MagicMock()
    mock_response.json.return_value = {"meta": {"page": 2, "pageCount": 4}}
    inputs = {"response": mock_response}

    token = stream.next_page_token(**inputs)

    assert token == {"page": 3}


def test_next_page_token_is_none_when_last_page_reached(patch_base_class):
    stream = PaystackStream(start_date=START_DATE)
    mock_response = MagicMock()
    mock_response.json.return_value = {"meta": {"page": 4, "pageCount": 4}}
    inputs = {"response": mock_response}

    token = stream.next_page_token(**inputs)

    assert token is None


def test_next_page_token_is_none_when_no_pages_exist(patch_base_class):
    stream = PaystackStream(start_date=START_DATE)
    mock_response = MagicMock()
    mock_response.json.return_value = {"meta": {"page": 1, "pageCount": 0}}
    inputs = {"response": mock_response}

    token = stream.next_page_token(**inputs)

    assert token is None


def test_parse_response_generates_data(patch_base_class):
    stream = PaystackStream(start_date=START_DATE)
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": 1137850082}, {"id": 1137850097}]}
    inputs = {"response": mock_response}

    parsed = stream.parse_response(**inputs)
    first, second = next(parsed), next(parsed)

    assert first == {"id": 1137850082}
    assert second == {"id": 1137850097}


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
    stream = PaystackStream(start_date=START_DATE)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = PaystackStream(start_date=START_DATE)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
