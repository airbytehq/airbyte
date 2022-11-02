#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus


@pytest.mark.parametrize(
    "test_name, response_action, retry_in, error_message, expected_action, expected_backoff, expected_message",
    [
        ("test_fail_with_backoff", ResponseAction.FAIL, 10, "", None, None, ""),
        (
            "test_success_no_backoff_error_message",
            ResponseAction.FAIL,
            None,
            "custom error message",
            ResponseAction.FAIL,
            None,
            "custom error message",
        ),
        ("test_ignore_with_backoff", ResponseAction.IGNORE, 10, "", None, None, ""),
        ("test_success_no_backoff", ResponseAction.IGNORE, None, "", ResponseAction.IGNORE, None, ""),
        ("test_success_with_backoff", ResponseAction.SUCCESS, 10, "", None, None, ""),
        ("test_success_no_backoff", ResponseAction.SUCCESS, None, "", ResponseAction.SUCCESS, None, ""),
        ("test_retry_with_backoff", ResponseAction.RETRY, 10, "", ResponseAction.RETRY, 10, ""),
        ("test_retry_no_backoff", ResponseAction.RETRY, None, "", ResponseAction.RETRY, None, ""),
    ],
)
def test_response_status(test_name, response_action, retry_in, error_message, expected_action, expected_backoff, expected_message):
    if expected_action or expected_backoff or expected_message:
        response_status = ResponseStatus(response_action, retry_in, error_message)
        assert (
            response_status.action == expected_action
            and response_status.retry_in == expected_backoff
            and response_status.error_message == expected_message
        )
    else:
        try:
            ResponseStatus(response_action, retry_in)
            assert False
        except ValueError:
            pass
