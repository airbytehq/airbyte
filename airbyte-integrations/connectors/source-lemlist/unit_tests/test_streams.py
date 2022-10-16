#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
import responses
from source_lemlist.streams import LemlistStream


def setup_responses():
    responses.add(
        responses.GET,
        "https://api.lemlist.com/api/example_endpoint",
        json=[
            {"_id": "cam_aaWL92T22Sei3Bz6v", "name": "Campaign1", "labels": ["label 1", "label 2"]},
            {"_id": "cam_aaXwBiebA8pWPKqpK", "name": "Campaign2"},
        ],
    )


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(LemlistStream, "path", "v0/example_endpoint")
    mocker.patch.object(LemlistStream, "primary_key", "test_primary_key")
    mocker.patch.object(LemlistStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = LemlistStream()
    inputs = {
        "stream_slice": None,
        "stream_state": None,
        "next_page_token": {"offset": 100},
    }
    expected_params = {"limit": stream.page_size, "offset": 100}
    assert stream.request_params(**inputs) == expected_params


@responses.activate
def test_next_page_token(patch_base_class):
    setup_responses()
    stream = LemlistStream()
    inputs = {"response": requests.get("https://api.lemlist.com/api/example_endpoint")}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


@responses.activate
def test_parse_response(patch_base_class):
    setup_responses()
    stream = LemlistStream()
    inputs = {"response": requests.get("https://api.lemlist.com/api/example_endpoint")}
    expected_parsed_object = {"_id": "cam_aaWL92T22Sei3Bz6v", "name": "Campaign1", "labels": ["label 1", "label 2"]}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = LemlistStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 100}}
    assert stream.request_headers(**inputs) == {}


def test_http_method(patch_base_class):
    stream = LemlistStream()
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
    stream = LemlistStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = LemlistStream()
    expected_backoff_time = 2
    assert stream.backoff_time(response_mock) == expected_backoff_time
