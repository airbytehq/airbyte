#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_breezy.source import BreezyStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(BreezyStream, "path", "v0/example_endpoint")
    mocker.patch.object(BreezyStream, "primary_key", "test_primary_key")
    mocker.patch.object(BreezyStream, "__abstractmethods__", set())


# def test_request_params(patch_base_class):
#     stream = BreezyStream()
#     # TODO: replace this with your input parameters
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     # TODO: replace this with your expected request parameters
#     expected_params = {}
#     assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = BreezyStream(limit=1, page_size=1)
    # TODO: replace this with your input parameters
    # val = {"total": 10}
    mock = MagicMock(json=lambda: {"total": 10, "data": []})
    # mock.json.__getitem__.side_effect = val.__getitem__
    # mock.__gt__ = lambda self, compare: True
    inputs = {"response": mock}
    # TODO: replace this with your expected next page token
    expected_token = {"limit": 1, "skip": 0}
    assert stream.next_page_token(**inputs) == expected_token


# def test_parse_response(patch_base_class):
#     stream = BreezyStream()
#     # TODO: replace this with your input parameters
#     inputs = {"response": MagicMock()}
#     # TODO: replace this with your expected parced object
#     expected_parsed_object = {}
#     assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = BreezyStream(limit=200, page_size=10, cookie="abcd", company="abcde")
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request headers
    expected_headers = {"cookie": "abcd", "origin": "https://app.breezy.hr"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = BreezyStream()
    expected_method = "POST"
    assert stream.http_method == expected_method


# @pytest.mark.parametrize(
#     ("http_status", "should_retry"),
#     [
#         (HTTPStatus.OK, False),
#         (HTTPStatus.BAD_REQUEST, False),
#         (HTTPStatus.TOO_MANY_REQUESTS, True),
#         (HTTPStatus.INTERNAL_SERVER_ERROR, True),
#     ],
# )
# def test_should_retry(patch_base_class, http_status, should_retry):
#     response_mock = MagicMock()
#     response_mock.status_code = http_status
#     stream = BreezyStream()
#     assert stream.should_retry(response_mock) == should_retry


# def test_backoff_time(patch_base_class):
#     response_mock = MagicMock()
#     stream = BreezyStream()
#     expected_backoff_time = None
#     assert stream.backoff_time(response_mock) == expected_backoff_time
