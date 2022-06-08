#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_webflow.source import CollectionItems, WebflowStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(WebflowStream, "path", "v0/example_endpoint")
    mocker.patch.object(WebflowStream, "primary_key", "test_primary_key")
    mocker.patch.object(WebflowStream, "__abstractmethods__", set())


def test_request_params_of_collection_items(patch_base_class):
    stream = CollectionItems()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 1}}
    expected_params = {"limit": 100, "offset": 1}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token_of_collection_items(patch_base_class):
    stream = CollectionItems()
    response_data = {"items": [{"item1_key": "item1_val"}], "count": 10, "offset": 100}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    expected_token = {"offset": 110}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response_of_collection_items(patch_base_class):
    stream = CollectionItems()
    mock_record = {"item1_key": "item1_val"}
    response_data = {"items": [mock_record]}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    parsed_item = next(stream.parse_response(**inputs))
    assert parsed_item == mock_record


def test_http_method(patch_base_class):
    stream = WebflowStream()
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
    stream = WebflowStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = WebflowStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
