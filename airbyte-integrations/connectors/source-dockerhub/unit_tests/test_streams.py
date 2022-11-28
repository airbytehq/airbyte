#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import requests
from source_dockerhub.source import DockerHub


def test_next_page_token():
    stream = DockerHub(jwt="foo", config={"docker_username": "foo"})

    # mocking the request with a response that has a next page token
    response = requests.Response()
    response.url = "https://foo"
    response.json = MagicMock()
    response.json.return_value = {"next": "https://foo?page=2"}
    inputs = {"response": response}

    expected_token = "?page=2"  # expected next page token
    assert stream.next_page_token(**inputs) == expected_token


# cant get this to work - TypeError: 'list' object is not an iterator
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


def test_request_headers():
    stream = DockerHub(jwt="foo", config={"docker_username": "foo"})

    inputs = {
        "stream_state": MagicMock(),
        "stream_slice": MagicMock(),
        "next_page_token": MagicMock(),
    }

    expected_headers = {"Authorization": "foo"}
    assert stream.request_headers(**inputs) == expected_headers
