#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import components
import pytest
import requests
from components import AmazonSPOauthAuthenticator, AmazonSPRdtAuthenticator


@pytest.fixture(autouse=True)
def reset_authenticator_instances():
    """Reset the module-level authenticator instances before and after each test."""
    components._authenticator_instances.clear()
    yield
    components._authenticator_instances.clear()


def _make_authenticator(
    cls=AmazonSPOauthAuthenticator,
    refresh_token_error_status_codes=(400,),
    refresh_token_error_key="error",
    refresh_token_error_values=("invalid_grant", "invalid_client", "unauthorized_client"),
):
    """Create an authenticator instance with refresh token error fields set, bypassing full init."""
    auth = object.__new__(cls)
    auth.config = {
        "lwa_app_id": "test-client-id",
        "lwa_client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
        "endpoint": "https://sellingpartnerapi-na.amazon.com",
    }

    mock_host = MagicMock()
    mock_host.eval.return_value = "sellingpartnerapi-na.amazon.com"
    auth._host = mock_host

    # Initialize the AbstractOauth2Authenticator fields that _wrap_refresh_token_exception reads
    auth._refresh_token_error_status_codes = refresh_token_error_status_codes
    auth._refresh_token_error_key = refresh_token_error_key
    auth._refresh_token_error_values = refresh_token_error_values

    return auth


def _make_http_error(status_code, json_body):
    """Create a requests.exceptions.HTTPError with a mocked response."""
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(json_body).encode("utf-8")
    error = requests.exceptions.HTTPError(response=response)
    return error


@pytest.mark.parametrize(
    "status_code,response_body,expected_is_refresh_error",
    [
        pytest.param(
            400,
            {"error": "invalid_grant", "error_description": "The refresh token is invalid or expired."},
            True,
            id="400_invalid_grant_is_config_error",
        ),
        pytest.param(
            400,
            {"error": "invalid_client", "error_description": "Client authentication failed."},
            True,
            id="400_invalid_client_is_config_error",
        ),
        pytest.param(
            400,
            {"error": "unauthorized_client", "error_description": "The client is not authorized."},
            True,
            id="400_unauthorized_client_is_config_error",
        ),
        pytest.param(
            400,
            {"error": "invalid_scope", "error_description": "The requested scope is invalid."},
            False,
            id="400_invalid_scope_is_not_config_error",
        ),
        pytest.param(
            401,
            {"error": "invalid_grant", "error_description": "The refresh token is invalid."},
            False,
            id="401_not_in_status_codes_not_config_error",
        ),
        pytest.param(
            500,
            {"error": "server_error"},
            False,
            id="500_server_error_not_config_error",
        ),
        pytest.param(
            400,
            {"message": "Bad Request"},
            False,
            id="400_no_error_key_not_config_error",
        ),
    ],
)
def test_wrap_refresh_token_exception(status_code, response_body, expected_is_refresh_error):
    """Verify that _wrap_refresh_token_exception correctly identifies OAuth refresh token errors
    based on the configured status codes, error key, and error values."""
    auth = _make_authenticator(cls=AmazonSPOauthAuthenticator)
    error = _make_http_error(status_code, response_body)

    result = auth._wrap_refresh_token_exception(error)

    assert result == expected_is_refresh_error


def test_wrap_refresh_token_exception_rdt_authenticator():
    """Verify that AmazonSPRdtAuthenticator also classifies 400 invalid_grant as a refresh token error."""
    auth = _make_authenticator(cls=AmazonSPRdtAuthenticator)
    error = _make_http_error(400, {"error": "invalid_grant", "error_description": "Token expired."})

    result = auth._wrap_refresh_token_exception(error)

    assert result is True


def test_default_empty_config_does_not_match():
    """Without refresh_token_error fields configured, no 400 error is classified as a refresh token error."""
    auth = _make_authenticator(
        refresh_token_error_status_codes=(),
        refresh_token_error_key="",
        refresh_token_error_values=(),
    )
    error = _make_http_error(400, {"error": "invalid_grant"})

    result = auth._wrap_refresh_token_exception(error)

    assert result is False
