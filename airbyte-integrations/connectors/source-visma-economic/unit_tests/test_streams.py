#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_visma_economic.source import VismaEconomicStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(VismaEconomicStream, "path", "v0/example_endpoint")
    mocker.patch.object(VismaEconomicStream, "primary_key", "test_primary_key")
    mocker.patch.object(VismaEconomicStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = VismaEconomicStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"pagesize": 1000, "skippages": 0}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = VismaEconomicStream()
    response = MagicMock(requests.Response)
    json = {
        "pagination": {
            "maxPageSizeAllowed": 1000,
            "skipPages": 0,
            "pageSize": 100,
            "results": 200,
            "resultsWithoutFilter": 200,
            "firstPage": "https://restapi.e-conomic.com/stream?skippages=0&pagesize=100",
            "nextPage": "https://restapi.e-conomic.com/stream?skippages=1&pagesize=100",
            "lastPage": "https://restapi.e-conomic.com/stream?skippages=1&pagesize=100",
        }
    }
    response.json = MagicMock(return_value=json)
    inputs = {"response": response}

    expected_token = {"skippages": ["1"], "pagesize": ["100"]}
    assert stream.next_page_token(**inputs) == expected_token


def test_no_next_page_token(patch_base_class):
    stream = VismaEconomicStream()
    response = MagicMock(requests.Response)
    response.json = MagicMock(return_value={})
    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_request_headers(patch_base_class):
    stream = VismaEconomicStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"X-AgreementGrantToken": None, "X-AppSecretToken": None}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = VismaEconomicStream()
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
    stream = VismaEconomicStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = VismaEconomicStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
