#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_persistiq.source import PersistiqStream


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse(json_data=kwargs["json_data"], status_code=kwargs["status_code"])


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PersistiqStream, "path", "v0/example_endpoint")
    mocker.patch.object(PersistiqStream, "primary_key", "test_primary_key")
    mocker.patch.object(PersistiqStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = PersistiqStream(api_key="mybeautifulkey")
    inputs = {"next_page_token": {"page": 1}}
    expected_params = {"page": 1}
    assert stream.request_params(stream_state=None, **inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = PersistiqStream(api_key="mybeautifulkey")
    # With next page
    response = mocked_requests_get(json_data={"has_more": True, "next_page": "https://api.persistiq.com/v1/users?page=2"}, status_code=200)
    expected_token = "2"
    assert stream.next_page_token(response=response) == {"page": expected_token}
    # Without next page
    response = mocked_requests_get(json_data={}, status_code=200)
    expected_token = None
    assert stream.next_page_token(response=response) == expected_token


def test_parse_response(patch_base_class):
    stream = PersistiqStream(api_key="mybeautifulkey")
    response = mocked_requests_get(json_data={"users": [{"id": 1, "name": "John Doe"}]}, status_code=200)
    expected_parsed_object = {"users": [{"id": 1, "name": "John Doe"}]}
    assert next(stream.parse_response(response=response)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = PersistiqStream(api_key="mybeautifulkey")
    expected_headers = {"x-api-key": "mybeautifulkey"}
    assert stream.request_headers() == expected_headers


def test_http_method(patch_base_class):
    stream = PersistiqStream(api_key="mybeautifulkey")
    expected_method = "GET"
    assert stream.http_method == expected_method
