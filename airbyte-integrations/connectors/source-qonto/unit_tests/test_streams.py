#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from source_qonto.source import QontoStream, Transactions


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(QontoStream, "path", "v0/example_endpoint")
    mocker.patch.object(QontoStream, "primary_key", "test_primary_key")

    def __mocked_init__(self):
        self.stream_name = "test_stream_name"
        pass

    mocker.patch.object(QontoStream, "__init__", __mocked_init__)


# Base Class
def test_request_params(patch_base_class):

    stream = QontoStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = QontoStream()
    simple_page_response_json = {
        "transactions": [],
        "meta": {"current_page": 1, "next_page": None, "prev_page": None, "total_pages": 3, "total_count": 210, "per_page": 100},
    }
    multiple_page_response_json = {
        "transactions": [],
        "meta": {"current_page": 5, "next_page": 6, "prev_page": 4, "total_pages": 7, "total_count": 210, "per_page": 100},
    }
    with patch.object(requests.Response, "json", return_value=simple_page_response_json):
        inputs = {"response": requests.Response()}
        expected_token = None
        assert stream.next_page_token(**inputs) == expected_token

    with patch.object(requests.Response, "json", return_value=multiple_page_response_json):
        inputs = {"response": requests.Response()}
        expected_token = {"current_page": 6}
        assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = QontoStream()
    mock_response_json = {
        "test_stream_name": [
            {"id": "171dba70-c75f-4337-b419-377a59bc9cf3", "name": "Fantastic Marble Wallet", "parent_id": None},
            {
                "id": "2487a014-618f-40e3-8a1f-eb76e883efc5",
                "name": "Fantastic Bronze Computer",
                "parent_id": "171dba70-c75f-4337-b419-377a59bc9cf3",
            },
        ],
        "meta": {"current_page": 1, "next_page": None, "prev_page": None, "total_pages": 1, "total_count": 2, "per_page": 100},
    }
    with patch.object(requests.Response, "json", return_value=mock_response_json):
        inputs = {"response": requests.Response()}
        expected_parsed_object = {"id": "171dba70-c75f-4337-b419-377a59bc9cf3", "name": "Fantastic Marble Wallet", "parent_id": None}
        assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = QontoStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = QontoStream()
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
    stream = QontoStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = QontoStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


# Transactions Class
def test_transactions_request_params():
    mocked_config = {
        "organization_slug": "test_slug",
        "secret_key": "test_key",
        "iban": "FRXXXXXXXXXXXXXXXXXXXXXXXXX",
        "start_date": "2022-06-01",
    }
    stream = Transactions(mocked_config)

    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"iban": stream.iban, "settled_at_from": stream.start_date}
    assert stream.request_params(**inputs) == expected_params

    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"current_page": 6}}
    expected_params = {"iban": stream.iban, "settled_at_from": stream.start_date, "current_page": 6}
    assert stream.request_params(**inputs) == expected_params
