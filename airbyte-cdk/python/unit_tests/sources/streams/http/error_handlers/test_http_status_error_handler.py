#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest
from unittest.mock import MagicMock
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import HttpStatusErrorHandler, ResponseAction

logger = MagicMock()

def test_given_ok_response_http_status_error_handler_returns_none():
    response = requests.Response()
    response.status_code = 200
    action, failure_type, error_message =  HttpStatusErrorHandler(logger).interpret_response(response)
    assert action == None
    assert failure_type == None
    assert error_message == None

@pytest.mark.parametrize(
    "error, expected_action, expected_failure_type, expected_error_message",
    [
        (403, ResponseAction.FAIL, FailureType.config_error, None),
        (404, ResponseAction.FAIL, FailureType.system_error, None),
        (508, ResponseAction.RETRY, FailureType.transient_error, "Unexpected 'HTTP Status Code' in error handler: 508"),
    ]
)
def test_given_error_code_in_response_http_status_error_handler_returns_expected_actions(error, expected_action, expected_failure_type, expected_error_message):
    response = requests.Response()
    response.status_code = error
    print('\n\n============\n\n')
    print(response)
    print('\n\n============\n\n')
    action, failure_type, error_message =  HttpStatusErrorHandler(logger).interpret_response(response)
    assert action == expected_action
    assert failure_type == expected_failure_type
    assert error_message == expected_error_message

def test_given_no_response_argument_returns_expected_action():

    action, failure_type, error_message = HttpStatusErrorHandler(logger).interpret_response()

    assert action == ResponseAction.RETRY
    assert failure_type == FailureType.transient_error
    assert error_message == None
