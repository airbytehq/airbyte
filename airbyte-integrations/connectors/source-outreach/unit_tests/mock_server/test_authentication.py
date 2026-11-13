# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .request_builder import OutreachRequestBuilder
from .response_builder import page_response, resource, token_response
from .utils import read_stream, record_ids


# The authenticator and error handler are shared by every stream, so these tests run on `accounts` only.
_STREAM = "accounts"
_FIRST_TOKEN = "test-access-token"
_REFRESHED_TOKEN = "refreshed-access-token"


def _expired_access_token() -> HttpResponse:
    # Body captured from the failed sync in the issue: Outreach returns the error object at the top level here.
    return HttpResponse(
        body=json.dumps(
            {"id": "expiredAccessToken", "title": "Expired Access Token", "detail": "Please get a new access token and try again."}
        ),
        status_code=401,
    )


def _with_token(url: str, token: str) -> HttpRequest:
    return HttpRequest(url, headers={"Authorization": f"Bearer {token}"})


# The retry after a refresh goes through the exponential backoff; skip the real wait.
@patch("time.sleep", lambda _seconds: None)
class TestAuthentication(TestCase):
    @HttpMocker()
    def test_401_mid_sync_refreshes_the_access_token_and_retries_the_page(self, http_mocker: HttpMocker) -> None:
        # Outreach can reject an access token as expired mid-sync, before the connector's tracked expiry. The sync
        # must refresh the token and retry the rejected page with the new token instead of failing.
        token_request = OutreachRequestBuilder.token_request()
        http_mocker.post(token_request, [token_response(_FIRST_TOKEN), token_response(_REFRESHED_TOKEN)])
        next_url = OutreachRequestBuilder.endpoint("/accounts").next_page_url("eyJzcCI6InVwZGF0ZWRBdCJ9")
        http_mocker.get(
            OutreachRequestBuilder.endpoint("/accounts").build(),
            page_response([resource(1, "account", {"name": "Acme", "updatedAt": "2024-01-02T03:04:05.000Z"})], next_url=next_url),
        )
        rejected_page = _with_token(next_url, _FIRST_TOKEN)
        retried_page = _with_token(next_url, _REFRESHED_TOKEN)
        http_mocker.get(rejected_page, _expired_access_token())
        http_mocker.get(
            retried_page,
            page_response([resource(2, "account", {"name": "Globex", "updatedAt": "2024-01-03T03:04:05.000Z"})]),
        )

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1, 2]
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(rejected_page, 1)
        http_mocker.assert_number_of_calls(retried_page, 1)

    @HttpMocker()
    def test_401_after_a_refresh_fails_as_config_error_without_refreshing_again(self, http_mocker: HttpMocker) -> None:
        token_request = OutreachRequestBuilder.token_request()
        http_mocker.post(token_request, [token_response(_FIRST_TOKEN), token_response(_REFRESHED_TOKEN)])
        accounts_request = OutreachRequestBuilder.endpoint("/accounts").build()
        http_mocker.get(accounts_request, [_expired_access_token(), _expired_access_token()])

        output = read_stream(_STREAM, SyncMode.full_refresh, expecting_exception=True)

        assert output.records == []
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == "Refreshed OAuth access token is rejected by the API."
        assert output.errors[0].trace.error.internal_message.endswith(
            "Error handler message: 'Outreach rejected the access token: Please get a new access token and try again. "
            "The connector refreshes the token and retries the request once. If this keeps failing, re-authenticate the source.'"
        )
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(accounts_request, 2)
