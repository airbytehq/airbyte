# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for Salesforce OAuth token-refresh error handling.

The connector authenticates to Pardot through Salesforce OAuth. When Salesforce
rejects the token refresh with a 400, the login requester must distinguish:

- ``expired access/refresh token``: the refresh token is expired or revoked, so
  the sync fails fast as a config_error telling the user to update it.
- ``token request is already being processed``: a transient concurrency
  rejection, so the request is retried instead of failing.
- Any other 400 body keeps the default behavior (system_error, no retry).
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase
from unittest.mock import patch

from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_STREAM_NAME = "users"

_LOGIN_REQUEST_BODY = "client_id=client-id&grant_type=refresh_token&client_secret=client-secret&refresh_token=refresh-token"
_LOGIN_REQUEST = HttpRequest("https://login.salesforce.com/services/oauth2/token", body=_LOGIN_REQUEST_BODY)
_USERS_REQUEST = HttpRequest("https://pi.pardot.com/api/v5/objects/users", query_params=ANY_QUERY_PARAMS)

_CONFIG = {
    "pardot_business_unit_id": "business-unit-id",
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "refresh-token",
    "is_sandbox": False,
    "start_date": "2021-01-01T00:00:00Z",
}

_REFRESH_TOKEN_ERROR_MESSAGE = (
    "The Salesforce refresh token is expired or revoked. Generate a new refresh token and update it in the source configuration."
)

_EXPIRED_REFRESH_TOKEN_BODY = {
    "error": "invalid_grant",
    "error_description": "expired access/refresh token",
}
_CONCURRENT_TOKEN_REQUEST_BODY = {
    "error": "invalid_grant",
    "error_description": "token request is already being processed",
}
_INVALID_CLIENT_BODY = {
    "error": "invalid_client",
    "error_description": "invalid client credentials",
}


def _login_response(body: Dict[str, Any], status_code: int) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _successful_login_response() -> HttpResponse:
    return _login_response(
        {"access_token": "access-token", "token_type": "Bearer", "expires_in": 3600},
        status_code=200,
    )


def _users_response() -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"values": [{"id": 1, "email": "user@airbyte.io", "updatedAt": "2025-01-01T00:00:00Z"}]}),
        status_code=200,
    )


def _read_users() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


def _failure_type(output: EntrypointOutput) -> Optional[FailureType]:
    assert output.errors, "expected at least one error trace message"
    return output.errors[0].trace.error.failure_type


class LoginErrorHandlingTest(TestCase):
    @HttpMocker()
    def test_expired_refresh_token_is_config_error(self, http_mocker: HttpMocker):
        http_mocker.post(_LOGIN_REQUEST, _login_response(_EXPIRED_REFRESH_TOKEN_BODY, status_code=400))

        output = _read_users()

        assert _failure_type(output) == FailureType.config_error
        assert output.errors[0].trace.error.message == _REFRESH_TOKEN_ERROR_MESSAGE
        http_mocker.assert_number_of_calls(_LOGIN_REQUEST, 1)

    @HttpMocker()
    def test_concurrent_token_request_is_retried_then_succeeds(self, http_mocker: HttpMocker):
        http_mocker.post(
            _LOGIN_REQUEST,
            [
                _login_response(_CONCURRENT_TOKEN_REQUEST_BODY, status_code=400),
                _successful_login_response(),
            ],
        )
        http_mocker.get(_USERS_REQUEST, _users_response())

        with patch("time.sleep"):
            output = _read_users()

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(_LOGIN_REQUEST, 2)

    @HttpMocker()
    def test_concurrent_token_request_exhausting_retries_is_not_config_error(self, http_mocker: HttpMocker):
        http_mocker.post(_LOGIN_REQUEST, _login_response(_CONCURRENT_TOKEN_REQUEST_BODY, status_code=400))

        with patch("time.sleep"):
            output = _read_users()

        assert _failure_type(output) != FailureType.config_error
        # default max_retries (5) + the initial attempt
        http_mocker.assert_number_of_calls(_LOGIN_REQUEST, 6)

    @HttpMocker()
    def test_other_400_keeps_default_behavior(self, http_mocker: HttpMocker):
        http_mocker.post(_LOGIN_REQUEST, _login_response(_INVALID_CLIENT_BODY, status_code=400))

        output = _read_users()

        assert _failure_type(output) == FailureType.system_error
        assert output.errors[0].trace.error.message != _REFRESH_TOKEN_ERROR_MESSAGE
        http_mocker.assert_number_of_calls(_LOGIN_REQUEST, 1)
