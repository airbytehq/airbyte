#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.http_logger import format_http_message

A_TITLE = "a title"
A_DESCRIPTION = "a description"
A_STREAM_NAME = "a stream name"
ANY_REQUEST = requests.Request(method="POST", url="http://a-url.com", headers={}, params={}).prepare()


class ResponseBuilder:
    def __init__(self):
        self._body_content = ""
        self._headers = {}
        self._request = ANY_REQUEST
        self._status_code = 100

    def body_content(self, body_content: bytes) -> "ResponseBuilder":
        self._body_content = body_content
        return self

    def headers(self, headers: dict) -> "ResponseBuilder":
        self._headers = headers
        return self

    def request(self, request: requests.PreparedRequest) -> "ResponseBuilder":
        self._request = request
        return self

    def status_code(self, status_code: int) -> "ResponseBuilder":
        self._status_code = status_code
        return self

    def build(self):
        response = requests.Response()
        response._content = self._body_content
        response.headers = self._headers
        response.request = self._request
        response.status_code = self._status_code
        return response


EMPTY_RESPONSE = {"body": {"content": ""}, "headers": {}, "status_code": 100}


@pytest.mark.parametrize(
    "test_name, http_method, url, headers, params, body_json, body_data, expected_airbyte_message",
    [
        (
            "test_basic_get_request",
            "GET",
            "https://airbyte.io",
            {},
            {},
            {},
            {},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {"method": "GET", "body": {"content": None}, "headers": {}},
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/"},
            },
        ),
        (
            "test_get_request_with_headers",
            "GET",
            "https://airbyte.io",
            {"h1": "v1", "h2": "v2"},
            {},
            {},
            {},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {"method": "GET", "body": {"content": None}, "headers": {"h1": "v1", "h2": "v2"}},
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/"},
            },
        ),
        (
            "test_get_request_with_request_params",
            "GET",
            "https://airbyte.io",
            {},
            {"p1": "v1", "p2": "v2"},
            {},
            {},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {"method": "GET", "body": {"content": None}, "headers": {}},
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/?p1=v1&p2=v2"},
            },
        ),
        (
            "test_get_request_with_request_body_json",
            "GET",
            "https://airbyte.io",
            {"Content-Type": "application/json"},
            {},
            {"b1": "v1", "b2": "v2"},
            {},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {
                        "method": "GET",
                        "body": {"content": '{"b1": "v1", "b2": "v2"}'},
                        "headers": {"Content-Type": "application/json", "Content-Length": "24"},
                    },
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/"},
            },
        ),
        (
            "test_get_request_with_headers_params_and_body",
            "GET",
            "https://airbyte.io",
            {"Content-Type": "application/json", "h1": "v1"},
            {"p1": "v1", "p2": "v2"},
            {"b1": "v1", "b2": "v2"},
            {},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {
                        "method": "GET",
                        "body": {"content": '{"b1": "v1", "b2": "v2"}'},
                        "headers": {"Content-Type": "application/json", "Content-Length": "24", "h1": "v1"},
                    },
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/?p1=v1&p2=v2"},
            },
        ),
        (
            "test_get_request_with_request_body_data",
            "GET",
            "https://airbyte.io",
            {"Content-Type": "application/x-www-form-urlencoded"},
            {},
            {},
            {"b1": "v1", "b2": "v2"},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {
                        "method": "GET",
                        "body": {"content": "b1=v1&b2=v2"},
                        "headers": {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": "11"},
                    },
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/"},
            },
        ),
        (
            "test_basic_post_request",
            "POST",
            "https://airbyte.io",
            {},
            {},
            {},
            {},
            {
                "airbyte_cdk": {"stream": {"name": A_STREAM_NAME}},
                "http": {
                    "title": A_TITLE,
                    "description": A_DESCRIPTION,
                    "request": {"method": "POST", "body": {"content": None}, "headers": {"Content-Length": "0"}},
                    "response": EMPTY_RESPONSE,
                },
                "log": {"level": "debug"},
                "url": {"full": "https://airbyte.io/"},
            },
        ),
    ],
)
def test_prepared_request_to_airbyte_message(test_name, http_method, url, headers, params, body_json, body_data, expected_airbyte_message):
    request = requests.Request(method=http_method, url=url, headers=headers, params=params)
    if body_json:
        request.json = body_json
    if body_data:
        request.data = body_data
    prepared_request = request.prepare()

    actual_airbyte_message = format_http_message(ResponseBuilder().request(prepared_request).build(), A_TITLE, A_DESCRIPTION, A_STREAM_NAME)

    assert actual_airbyte_message == expected_airbyte_message


@pytest.mark.parametrize(
    "test_name, response_body, response_headers, status_code, expected_airbyte_message",
    [
        ("test_response_no_body_no_headers", b"", {}, 200, {"body": {"content": ""}, "headers": {}, "status_code": 200}),
        (
            "test_response_no_body_with_headers",
            b"",
            {"h1": "v1", "h2": "v2"},
            200,
            {"body": {"content": ""}, "headers": {"h1": "v1", "h2": "v2"}, "status_code": 200},
        ),
        (
            "test_response_with_body_no_headers",
            b'{"b1": "v1", "b2": "v2"}',
            {},
            200,
            {"body": {"content": '{"b1": "v1", "b2": "v2"}'}, "headers": {}, "status_code": 200},
        ),
        (
            "test_response_with_body_and_headers",
            b'{"b1": "v1", "b2": "v2"}',
            {"h1": "v1", "h2": "v2"},
            200,
            {"body": {"content": '{"b1": "v1", "b2": "v2"}'}, "headers": {"h1": "v1", "h2": "v2"}, "status_code": 200},
        ),
    ],
)
def test_response_to_airbyte_message(test_name, response_body, response_headers, status_code, expected_airbyte_message):
    response = ResponseBuilder().body_content(response_body).headers(response_headers).status_code(status_code).build()

    actual_airbyte_message = format_http_message(response, A_TITLE, A_DESCRIPTION, A_STREAM_NAME)

    assert actual_airbyte_message["http"]["response"] == expected_airbyte_message
