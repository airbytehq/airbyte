#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import patch

import pytest
import requests
from source_hubspot.errors import HubspotInvalidAuth
from source_hubspot.streams import Stream


# Define a mock function to be used with backoff.on_exception
def mock_retry_func(*args, **kwargs):
    # Define the error message
    error_message = "Token expired"

    # Create a mock response with a 401 status code
    response = requests.Response()
    response.status_code = 401
    response._content = json.dumps({"message": error_message}).encode()

    # Raise the exception with the defined message
    raise HubspotInvalidAuth(error_message, response=response)


@patch.multiple(Stream, __abstractmethods__=set())
def test_handle_request_with_retry(common_params):
    # Create a mock instance of the Stream class
    stream_instance = Stream(**common_params)

    # Create a mock response
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps({"data": "Mocked response"}).encode()

    # Mock the _send_request method of the Stream class to return the mock response
    with patch.object(stream_instance, "_send_request", return_value=mock_response):
        response = stream_instance.handle_request()

    assert response.status_code == 200
    assert response.json() == {"data": "Mocked response"}


@patch.multiple(Stream, __abstractmethods__=set())
def test_handle_request_with_retry_token_expired(common_params):
    # Create a mock instance of the Stream class
    stream_instance = Stream(**common_params)

    # Mock the _send_request method of the Stream class to raise HubspotInvalidAuth exception
    with patch.object(stream_instance, "_send_request", side_effect=mock_retry_func) as mocked_send_request:
        with pytest.raises(HubspotInvalidAuth):
            stream_instance.handle_request()

    assert mocked_send_request.call_count == 5
