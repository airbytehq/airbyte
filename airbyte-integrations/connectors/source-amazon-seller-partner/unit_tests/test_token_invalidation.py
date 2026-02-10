#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import components
import pytest
import requests
from components import (
    TOKEN_EXPIRED_ERROR_MESSAGE,
    AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy,
    AmazonSPOauthAuthenticator,
)


@pytest.fixture(autouse=True)
def reset_authenticator_instance():
    """Reset the module-level authenticator instance before and after each test."""
    components._authenticator_instance = None
    yield
    components._authenticator_instance = None


def _create_response(status_code: int, json_body: dict) -> requests.Response:
    """Create a real requests.Response object with the given status code and JSON body."""
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(json_body).encode("utf-8")
    return response


@pytest.mark.parametrize(
    "status_code,response_body,authenticator_present,should_invalidate",
    [
        pytest.param(
            403,
            {"errors": [{"code": "Unauthorized", "message": "Access denied.", "details": TOKEN_EXPIRED_ERROR_MESSAGE}]},
            True,
            True,
            id="403_with_token_expired_in_details_invalidates_token",
        ),
        pytest.param(
            403,
            {"errors": [{"code": "Unauthorized", "message": TOKEN_EXPIRED_ERROR_MESSAGE, "details": ""}]},
            True,
            True,
            id="403_with_token_expired_in_message_invalidates_token",
        ),
        pytest.param(
            403,
            {"errors": [{"code": "Unauthorized", "message": "Access denied.", "details": "Some other error message"}]},
            True,
            False,
            id="403_with_different_error_message_no_invalidation",
        ),
        pytest.param(
            403,
            {"errors": [{"code": "Forbidden", "message": "You don't have permission."}]},
            True,
            False,
            id="403_without_details_field_no_invalidation",
        ),
        pytest.param(
            401,
            {"errors": [{"code": "Unauthorized", "message": "Access denied.", "details": TOKEN_EXPIRED_ERROR_MESSAGE}]},
            True,
            False,
            id="401_status_code_no_invalidation",
        ),
        pytest.param(
            500,
            {"errors": [{"code": "InternalError", "message": "Server error."}]},
            True,
            False,
            id="500_status_code_no_invalidation",
        ),
        pytest.param(
            200,
            {"payload": {"data": "success"}},
            True,
            False,
            id="200_status_code_no_invalidation",
        ),
        pytest.param(
            403,
            {"errors": [{"code": "Unauthorized", "message": "Access denied.", "details": TOKEN_EXPIRED_ERROR_MESSAGE}]},
            False,
            False,
            id="403_with_token_expired_but_no_authenticator_instance",
        ),
    ],
)
def test_check_and_invalidate_expired_token(
    status_code: int,
    response_body: dict,
    authenticator_present: bool,
    should_invalidate: bool,
):
    """
    Test that _check_and_invalidate_expired_token correctly identifies token expiration errors
    and invalidates the token only when appropriate.
    """
    mock_authenticator = MagicMock(spec=AmazonSPOauthAuthenticator)

    if authenticator_present:
        components._authenticator_instance = mock_authenticator

    response = _create_response(status_code, response_body)

    AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy._check_and_invalidate_expired_token(response)

    if should_invalidate:
        mock_authenticator.invalidate_token.assert_called_once()
    else:
        mock_authenticator.invalidate_token.assert_not_called()


@pytest.mark.parametrize(
    "response_or_exception",
    [
        pytest.param(None, id="none_value"),
        pytest.param(requests.RequestException("Connection error"), id="request_exception"),
        pytest.param("not a response", id="string_value"),
    ],
)
def test_check_and_invalidate_expired_token_with_non_response(response_or_exception):
    """
    Test that _check_and_invalidate_expired_token handles non-Response inputs gracefully.
    """
    mock_authenticator = MagicMock(spec=AmazonSPOauthAuthenticator)
    components._authenticator_instance = mock_authenticator

    AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy._check_and_invalidate_expired_token(response_or_exception)

    mock_authenticator.invalidate_token.assert_not_called()


def test_check_and_invalidate_expired_token_with_invalid_json():
    """
    Test that _check_and_invalidate_expired_token handles responses with invalid JSON gracefully.
    """
    mock_authenticator = MagicMock(spec=AmazonSPOauthAuthenticator)
    components._authenticator_instance = mock_authenticator

    response = requests.Response()
    response.status_code = 403
    response._content = b"not valid json"

    AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy._check_and_invalidate_expired_token(response)

    mock_authenticator.invalidate_token.assert_not_called()


def test_invalidate_token_sets_expiry_to_past():
    """
    Test that invalidate_token() calls set_token_expiry_date with a date in the past.
    """
    authenticator = object.__new__(AmazonSPOauthAuthenticator)

    with patch.object(authenticator, "set_token_expiry_date") as mock_set_expiry:
        authenticator.invalidate_token()

        mock_set_expiry.assert_called_once()
        expiry_date = mock_set_expiry.call_args[0][0]

        assert expiry_date.year == 1970
        assert expiry_date.month == 1
        assert expiry_date.day == 1
