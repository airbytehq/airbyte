#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from types import BuiltinFunctionType
from unittest.mock import MagicMock

import pytest
from source_vtex.source import VtexStream
from source_vtex.source import VtexAuthenticator
import datetime

START_DATE = "2021-10-27T00:00:00.000Z"
END_DATE = (datetime.datetime.now() + datetime.timedelta(hours=3)) \
            .strftime('%Y-%m-%dT%H:%M:%S.000Z')
 
def fake_authenticator():
    return VtexAuthenticator(
        'not', 'real', 'auth'
    )

def build_stream():
    stream = VtexStream(
        start_date=START_DATE,
        authenticator=fake_authenticator()
    )
    return stream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(VtexStream, "path", "v0/example_endpoint")
    mocker.patch.object(VtexStream, "primary_key", "test_primary_key")
    mocker.patch.object(VtexStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = build_stream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {
        'f_creationDate': f'creationDate:[{START_DATE} TO {END_DATE}]',
        'page': 1

    }
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    metadata_only_response = {
        "list": [
        ],
        "facets": [],
        "paging": {
            "total": 220,
            "pages": 15,
            "currentPage": 1,
            "perPage": 15
        },
        "stats": {
            "stats": {
                "totalValue": {
                    "Count": 220,
                    "Max": 0.0,
                    "Mean": 0.0,
                    "Min": 0.0,
                    "Missing": 0,
                    "StdDev": 0.0,
                    "Sum": 0.0,
                    "SumOfSquares": 0.0,
                    "Facets": {}
                },
                "totalItems": {
                    "Count": 220,
                    "Max": 0.0,
                    "Mean": 0.0,
                    "Min": 0.0,
                    "Missing": 0,
                    "StdDev": 0.0,
                    "Sum": 0.0,
                    "SumOfSquares": 0.0,
                    "Facets": {}
                }
            }
        },
        "reportRecordsLimit": 50000
    }
    stream = build_stream()
    
    
    response_mock = {}
    response_mock = MagicMock(status_code=201, json=lambda : metadata_only_response)
    inputs = {
        'response': response_mock
    }
    expected_token = {'page': 2}
    assert stream.next_page_token(**inputs) == expected_token


def test_http_method(patch_base_class):
    stream = build_stream()
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
    stream = build_stream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = build_stream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
