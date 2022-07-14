#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_discourse.streams import DiscourseStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(DiscourseStream, "path", "v0/example_endpoint")
    mocker.patch.object(DiscourseStream, "primary_key", "test_primary_key")
    mocker.patch.object(DiscourseStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = DiscourseStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_parse_response(patch_base_class):
    stream = DiscourseStream()
    mock_record = {}
    response_data = {"items": [mock_record]}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    parsed_item = next(stream.parse_response(**inputs))
    assert parsed_item == mock_record


def test_http_method(patch_base_class):
    stream = DiscourseStream()
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
    stream = DiscourseStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = DiscourseStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
