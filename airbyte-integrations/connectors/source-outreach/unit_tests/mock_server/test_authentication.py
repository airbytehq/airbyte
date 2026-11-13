# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .request_builder import OutreachRequestBuilder
from .response_builder import error_response, page_response, resource, token_response
from .test_error_handling import _Clock
from .utils import read_stream, record_ids


def _expired_token() -> HttpResponse:
    return error_response(401, "expiredAccessToken", "Expired Access Token", "Please get a new access token and try again.")


def _refreshed_token() -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": "refreshed-access-token", "expires_in": 7200}), status_code=200)


@pytest.mark.parametrize("stream,page_size", [("calls", 1000), ("mailings", 100)])
def test_mid_sync_401_refreshes_token_and_retries_the_same_page(stream: str, page_size: int) -> None:
    with HttpMocker() as http_mocker:
        builder = OutreachRequestBuilder.endpoint(f"/{stream}").with_page_size(page_size)
        first = builder.build()
        next_url = builder.next_page_url("page-two")
        expired = HttpRequest(next_url, headers={"Authorization": "Bearer test-access-token"})
        retried = HttpRequest(next_url, headers={"Authorization": "Bearer refreshed-access-token"})
        token = OutreachRequestBuilder.token_request()
        http_mocker.post(token, [token_response(), _refreshed_token()])
        http_mocker.get(first, page_response([resource(1, stream, {"updatedAt": "2024-01-02T03:04:05.000Z"})], next_url=next_url))
        http_mocker.get(expired, _expired_token())
        http_mocker.get(retried, page_response([resource(2, stream, {"updatedAt": "2024-01-03T03:04:05.000Z"})]))

        # The API rejects the token while the local two-hour lifetime is still valid.
        # Merely retrying would keep sending the same token.
        with _Clock():
            output = read_stream(stream, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1, 2]
        http_mocker.assert_number_of_calls(token, 2)
        for request in (first, expired, retried):
            http_mocker.assert_number_of_calls(request, 1)


def test_401_after_refresh_fails_without_refreshing_in_a_loop() -> None:
    with HttpMocker() as http_mocker:
        builder = OutreachRequestBuilder.endpoint("/calls")
        original = builder.build()
        retried = builder.build(access_token="refreshed-access-token")
        token = OutreachRequestBuilder.token_request()
        http_mocker.post(token, [token_response(), _refreshed_token()])
        http_mocker.get(original, _expired_token())
        http_mocker.get(retried, _expired_token())

        with _Clock():
            output = read_stream("calls", SyncMode.full_refresh, expecting_exception=True)

        assert not output.records
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == "Refreshed OAuth access token is rejected by the API."
        http_mocker.assert_number_of_calls(token, 2)
        http_mocker.assert_number_of_calls(original, 1)
        http_mocker.assert_number_of_calls(retried, 1)
