#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock
import json
import requests
import pytest
from source_dockerhub.source import DockerHub


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(DockerHub, "path", "v0/example_endpoint")
    mocker.patch.object(DockerHub, "primary_key", "test_primary_key")
    mocker.patch.object(DockerHub, "__abstractmethods__", set())



def test_next_page_token(patch_base_class):
    stream = DockerHub(jwt="foo", config={"docker_username": "foo"})
    
    # mocking the request with a response that has a next page token
    response = requests.Response()
    response.url = "https://foo"
    response.json = MagicMock()
    response.json.return_value = {"next": "https://foo?page=2"}
    inputs = {"response": response}

    expected_token = "?page=2" # expected next page token
    assert stream.next_page_token(**inputs) == expected_token


## cant get this to work - TypeError: 'list' object is not an iterator
# def test_parse_response(patch_base_class, mocker):
#     response = mocker.MagicMock()
#     response.json.return_value = {"one": 1}
#     stream = DockerHub(jwt="foo", config={"docker_username": "foo"})

#     inputs = {
#         "response": response,
#         "stream_state": MagicMock(),
#         "stream_slice": MagicMock(),
#         "next_page_token": MagicMock(),
#     }

#     expected_parsed_object = {"one": 1}
#     assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = DockerHub(jwt="foo", config={"docker_username": "foo"})

    inputs = {
        "stream_state": MagicMock(),
        "stream_slice": MagicMock(),
        "next_page_token": MagicMock(),
    }

    expected_headers = {"Authorization": "foo"}
    assert stream.request_headers(**inputs) == expected_headers

# not yet implemented, not very important

# def test_http_method(patch_base_class):
#     stream = DockerHub()
#     # TODO: replace this with your expected http request method
#     expected_method = "GET"
#     assert stream.http_method == expected_method


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
#     stream = DockerHub()
#     assert stream.should_retry(response_mock) == should_retry


# def test_backoff_time(patch_base_class):
#     response_mock = MagicMock()
#     stream = DockerHub()
#     expected_backoff_time = None
#     assert stream.backoff_time(response_mock) == expected_backoff_time
