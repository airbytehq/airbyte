# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source as get_source
from unit_tests.test_jsonapi_records import _BASE_URL, _CONFIG, _STREAMS, _TOKEN_URL, _legacy_flatten, _query_params, _resource, _response


_REFRESH_BODY = "grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token"
_EXPIRED_TOKEN_RESPONSE = HttpResponse(
    body=json.dumps(
        {
            "errors": [
                {"id": "expiredAccessToken", "title": "Expired Access Token", "detail": "Please get a new access token and try again."}
            ]
        }
    ),
    status_code=401,
)


def _token_response(token: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": token, "expires_in": 7200}), status_code=200)


def _mailings_request(token: str) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}{_STREAMS['mailings']['retriever']['requester']['path']}",
        query_params=_query_params("mailings"),
        headers={"Authorization": f"Bearer {token}"},
    )


def _read_mailings():
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.incremental).build()
    state = StateBuilder().build()
    return read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


def test_expired_access_token_mid_sync_is_refreshed_and_request_retried() -> None:
    mailing = _resource("mailing-1", {"subject": "hello", "updatedAt": "2021-01-01T00:00:00.000Z"})

    token_request = HttpRequest(_TOKEN_URL, body=_REFRESH_BODY)
    expired_request = _mailings_request("expired-token")
    fresh_request = _mailings_request("fresh-token")

    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, [_token_response("expired-token"), _token_response("fresh-token")])
        http_mocker.get(expired_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(fresh_request, _response([mailing]))

        output = _read_mailings()

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)

    assert not output.errors
    assert [record.record.data for record in output.records] == [_legacy_flatten(mailing)]


def test_access_token_rejected_after_refresh_fails_as_config_error() -> None:
    token_request = HttpRequest(_TOKEN_URL, body=_REFRESH_BODY)
    first_request = _mailings_request("revoked-token-1")
    refreshed_request = _mailings_request("revoked-token-2")

    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, [_token_response("revoked-token-1"), _token_response("revoked-token-2")])
        http_mocker.get(first_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(refreshed_request, _EXPIRED_TOKEN_RESPONSE)

        output = _read_mailings()

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(refreshed_request, 1)

    assert output.records == []
    stream_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor is not None]
    assert [(error.failure_type, error.message) for error in stream_errors] == [
        (FailureType.config_error, "Refreshed OAuth access token is rejected by the API.")
    ]
