#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, HttpStatusErrorHandler, ResponseAction

logger = MagicMock()


def test_given_ok_response_http_status_error_handler_returns_success_action(mocker):
    mocked_response = MagicMock(spec=requests.Response)
    mocked_response.ok = True
    mocked_response.status_code = 200
    error_resolution = HttpStatusErrorHandler(logger).interpret_response(mocked_response)
    assert isinstance(error_resolution, ErrorResolution)
    assert error_resolution.response_action == ResponseAction.SUCCESS
    assert error_resolution.failure_type is None
    assert error_resolution.error_message is None


@pytest.mark.parametrize(
    "error, expected_action, expected_failure_type, expected_error_message",
    [
        (403, ResponseAction.FAIL, FailureType.config_error, "Forbidden. You don't have permission to access this resource."),
        (404, ResponseAction.FAIL, FailureType.system_error, "Not found. The requested resource was not found on the server."),
    ],
)
def test_given_error_code_in_response_http_status_error_handler_returns_expected_actions(
    error, expected_action, expected_failure_type, expected_error_message
):
    response = requests.Response()
    response.status_code = error
    error_resolution = HttpStatusErrorHandler(logger).interpret_response(response)
    assert error_resolution.response_action == expected_action
    assert error_resolution.failure_type == expected_failure_type
    assert error_resolution.error_message == expected_error_message


def test_given_no_response_argument_returns_expected_action():

    error_resolution = HttpStatusErrorHandler(logger).interpret_response()

    assert error_resolution.response_action == ResponseAction.FAIL
    assert error_resolution.failure_type == FailureType.system_error


def test_given_unmapped_status_error_returns_retry_action_as_transient_error():

    response = requests.Response()
    response.status_code = 508

    error_resolution = HttpStatusErrorHandler(logger).interpret_response(response)

    assert error_resolution.response_action == ResponseAction.RETRY
    assert error_resolution.failure_type == FailureType.system_error
    assert error_resolution.error_message == "Unexpected HTTP Status Code in error handler: 508"


def test_given_requests_exception_returns_retry_action_as_transient_error():

    error_resolution = HttpStatusErrorHandler(logger).interpret_response(requests.RequestException())

    assert error_resolution.response_action == ResponseAction.RETRY
    assert error_resolution.failure_type


def test_given_unmapped_exception_returns_retry_action_as_system_error():

    error_resolution = HttpStatusErrorHandler(logger).interpret_response(Exception())

    assert error_resolution.response_action == ResponseAction.RETRY
    assert error_resolution.failure_type == FailureType.system_error


def test_given_unexpected_response_type_returns_fail_action_as_system_error():

    error_resolution = HttpStatusErrorHandler(logger).interpret_response("unexpected response type")

    assert error_resolution.response_action == ResponseAction.FAIL
    assert error_resolution.failure_type == FailureType.system_error
    assert error_resolution.error_message == "Received unexpected response type: <class 'str'>"


def test_given_injected_error_mapping_returns_expected_action():

    default_error_handler = HttpStatusErrorHandler(logger)

    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 509
    mock_response.ok = False

    default_error_resolution = default_error_handler.interpret_response(mock_response)

    assert default_error_resolution.response_action == ResponseAction.RETRY
    assert default_error_resolution.failure_type == FailureType.system_error
    assert default_error_resolution.error_message == f"Unexpected HTTP Status Code in error handler: {mock_response.status_code}"

    mapped_error_resolution = ErrorResolution(
        response_action=ResponseAction.IGNORE, failure_type=FailureType.transient_error, error_message="Injected mapping"
    )

    error_mapping = {509: mapped_error_resolution}

    actual_error_resolution = HttpStatusErrorHandler(logger, error_mapping).interpret_response(mock_response)

    assert actual_error_resolution.response_action == mapped_error_resolution.response_action
    assert actual_error_resolution.failure_type == mapped_error_resolution.failure_type
    assert actual_error_resolution.error_message == mapped_error_resolution.error_message
