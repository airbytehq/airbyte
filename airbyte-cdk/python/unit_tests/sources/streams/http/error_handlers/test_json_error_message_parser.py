#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.streams.http.error_handlers import JsonErrorMessageParser


@pytest.mark.parametrize(
        "response_body,expected_error_message",
        [
            (b'{"message": "json error message"}', "json error message"),
            (b'[{"message": "list error message"}]', "list error message"),
            (b'[{"message": "list error message 1"}, {"message": "list error message 2"}]', "list error message 1, list error message 2"),
        ]

)
def test_given_error_message_in_response_body_parse_response_error_message_returns_error_message(response_body, expected_error_message):
    response = requests.Response()
    response._content = response_body
    error_message = JsonErrorMessageParser().parse_response_error_message(response)
    assert error_message == expected_error_message


def test_given_invalid_json_body_parse_response_error_message_returns_none():
    response = requests.Response()
    response._content = b'invalid json body'
    error_message = JsonErrorMessageParser().parse_response_error_message(response)
    assert error_message is None
