# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import urlencode

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source as get_source
from unit_tests.test_jsonapi_records import (
    _BASE_URL,
    _CONFIG,
    _STREAMS,
    _TOKEN_URL,
    _legacy_flatten,
    _query_params,
    _request,
    _resource,
    _response,
)


_TOKEN_REQUEST_BODY = "grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token"
_EXPIRED_TOKEN_RESPONSE = HttpResponse(
    body=json.dumps(
        {
            "errors": [
                {
                    "id": "expiredAccessToken",
                    "title": "Expired Access Token",
                    "detail": "Please get a new access token and try again.",
                }
            ]
        }
    ),
    status_code=401,
)


def _token_response(access_token: str) -> HttpResponse:
    # expires_in is long enough that the authenticator never refreshes proactively during the test,
    # so any refresh observed must come from the 401 handling.
    return HttpResponse(body=json.dumps({"access_token": access_token, "expires_in": 7200}), status_code=200)


def _mock_token_endpoint(http_mocker: HttpMocker, *access_tokens: str) -> HttpRequest:
    token_request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
    http_mocker.post(token_request, [_token_response(token) for token in access_tokens])
    return token_request


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _second_page_url(stream_name: str) -> str:
    return f"{_BASE_URL}{_STREAMS[stream_name]['retriever']['requester']['path']}?{urlencode({**_query_params(stream_name), 'page[number]': '2'})}"


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().build()
    return read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


@pytest.mark.parametrize("stream_name", ["mailings", "calls", "prospects"])
def test_expired_access_token_mid_sync_is_refreshed_and_request_retried(stream_name: str) -> None:
    first = _resource("1", {"updatedAt": "2021-01-01T00:00:00.000Z"})
    second = _resource("2", {"updatedAt": "2021-01-02T00:00:00.000Z"})
    next_url = _second_page_url(stream_name)

    with HttpMocker() as http_mocker:
        token_request = _mock_token_endpoint(http_mocker, "token-1", "token-2")
        first_page = HttpRequest(_request(stream_name)._parsed_url.geturl(), headers=_auth("token-1"))
        http_mocker.get(first_page, _response([first], links={"next": next_url}))
        # The API revokes token-1 server-side before the authenticator considers it expired.
        second_page_with_expired_token = HttpRequest(next_url, headers=_auth("token-1"))
        second_page_with_refreshed_token = HttpRequest(next_url, headers=_auth("token-2"))
        http_mocker.get(second_page_with_expired_token, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(second_page_with_refreshed_token, _response([second]))

        output = _read_stream(stream_name)

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(second_page_with_expired_token, 1)
        http_mocker.assert_number_of_calls(second_page_with_refreshed_token, 1)

    assert not output.errors
    assert [record.record.data for record in output.records] == [_legacy_flatten(first), _legacy_flatten(second)]
    assert output.state_messages[-1].state.stream.stream_state.updatedAt == "2021-01-02T00:00:00.000Z"


def test_access_token_still_rejected_after_refresh_fails_as_config_error_without_looping() -> None:
    stream_name = "mailings"
    request = _request(stream_name)

    with HttpMocker() as http_mocker:
        token_request = _mock_token_endpoint(http_mocker, "token-1", "token-2")
        http_mocker.get(request, _EXPIRED_TOKEN_RESPONSE)

        output = _read_stream(stream_name)

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(request, 2)

    assert output.records == []
    stream_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
    assert len(stream_errors) == 1
    error = stream_errors[0]
    assert error.stream_descriptor.name == stream_name
    assert error.failure_type == FailureType.config_error
    assert "rejected with status code '401' again after the OAuth token was refreshed" in error.internal_message
