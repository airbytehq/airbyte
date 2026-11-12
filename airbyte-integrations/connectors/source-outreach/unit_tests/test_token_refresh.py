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
    return HttpResponse(body=json.dumps({"access_token": access_token, "expires_in": 7200}), status_code=200)


def _authorized(url: str, access_token: str, query_params: dict | None = None) -> HttpRequest:
    return HttpRequest(url, query_params=query_params, headers={"Authorization": f"Bearer {access_token}"})


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().build()
    return read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


@pytest.mark.parametrize("stream_name", sorted(_STREAMS))
def test_expired_access_token_mid_sync_is_refreshed_and_request_retried(stream_name: str) -> None:
    """A 401 for an expired access token mid-sync forces a token refresh and retries the page with the new token."""
    path = _STREAMS[stream_name]["retriever"]["requester"]["path"]
    first = _resource("page-1", {"name": "first", "updatedAt": "2021-01-01T00:00:00.000Z"})
    second = _resource("page-2", {"name": "second", "updatedAt": "2021-01-02T00:00:00.000Z"})
    next_url = f"{_BASE_URL}{path}?{urlencode({**_query_params(stream_name), 'page[after]': 'cursor-2'})}"

    with HttpMocker() as http_mocker:
        token_request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
        http_mocker.post(token_request, [_token_response("token-1"), _token_response("token-2")])
        http_mocker.get(
            _authorized(f"{_BASE_URL}{path}", "token-1", _query_params(stream_name)),
            _response([first], links={"next": next_url}),
        )
        expired_second_page = _authorized(next_url, "token-1")
        http_mocker.get(expired_second_page, _EXPIRED_TOKEN_RESPONSE)
        refreshed_second_page = _authorized(next_url, "token-2")
        http_mocker.get(refreshed_second_page, _response([second]))

        output = _read_stream(stream_name)

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(refreshed_second_page, 1)

    assert not output.errors
    assert [record.record.data for record in output.records] == [_legacy_flatten(first), _legacy_flatten(second)]
    assert output.state_messages[-1].state.stream.stream_state.updatedAt == "2021-01-02T00:00:00.000Z"


def test_access_token_rejected_after_refresh_fails_as_config_error() -> None:
    """If the freshly refreshed token is also rejected, the sync fails fast with a config error instead of looping."""
    path = _STREAMS["accounts"]["retriever"]["requester"]["path"]

    with HttpMocker() as http_mocker:
        token_request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
        http_mocker.post(token_request, [_token_response("token-1"), _token_response("token-2")])
        http_mocker.get(_authorized(f"{_BASE_URL}{path}", "token-1", _query_params("accounts")), _EXPIRED_TOKEN_RESPONSE)
        rejected_after_refresh = _authorized(f"{_BASE_URL}{path}", "token-2", _query_params("accounts"))
        http_mocker.get(rejected_after_refresh, _EXPIRED_TOKEN_RESPONSE)

        output = _read_stream("accounts")

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(rejected_after_refresh, 1)

    assert output.records == []
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
