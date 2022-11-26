#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_lexware.source import LexwareStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(LexwareStream, "path", "voucherlist")
    mocker.patch.object(LexwareStream, "primary_key", "id")
    mocker.patch.object(LexwareStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = LexwareStream()
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request parameters
    expected_params = {'size': 1, 'sort': 'updatedDate,ASC'}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = LexwareStream()
    # TODO: replace this with your input parameters
    inputs = {"response": MagicMock()}
    # TODO: replace this with your expected next page token
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


# Mock response object
response_mock = MagicMock()
response_mock.json.return_value = {'abc':'def'}


def test_parse_response(patch_base_class):
    stream = LexwareStream()
    # TODO: replace this with your input parameters
    inputs = {'response': response_mock}
    # TODO: replace this with your expected parced object
    expected_parsed_object = {'abc': 'def'}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = LexwareStream()
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request headers
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = LexwareStream()
    # TODO: replace this with your expected http request method
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
    stream = LexwareStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = LexwareStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
