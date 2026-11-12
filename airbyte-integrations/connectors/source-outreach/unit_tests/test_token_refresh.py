# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch
from urllib.parse import urlencode

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source


_TOKEN_REQUEST = HttpRequest(
    "https://api.outreach.io/oauth/token",
    body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
)
_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2020-11-16T00:00:00Z",
}
# stream name -> (path, page size)
_STREAMS = {"mailings": ("mailings", "100"), "calls": ("calls", "1000")}
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


def _page(record_id: int, next_url: str | None = None) -> HttpResponse:
    body = {"data": [{"id": record_id, "type": "mailing", "attributes": {"updatedAt": f"2021-01-0{record_id}T00:00:00.000Z"}}]}
    if next_url:
        body["links"] = {"next": next_url}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _urls(stream_name: str) -> tuple[str, dict, str]:
    path, page_size = _STREAMS[stream_name]
    url = f"https://api.outreach.io/api/v2/{path}"
    query = {
        "count": "false",
        "sort": "updatedAt",
        "page[size]": page_size,
        "newFilterSyntax": "true",
        "filter[updatedAt][gte]": "2020-11-16T00:00:00.000Z",
    }
    next_url = f"{url}?{urlencode({**query, 'page[after]': 'cursor-2'})}"
    return url, query, next_url


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    state = StateBuilder().build()
    # The retry after the token refresh goes through the CDK's backoff; do not really sleep.
    with patch("time.sleep"):
        return read(build_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


@pytest.mark.parametrize("stream_name", sorted(_STREAMS))
def test_access_token_expiring_mid_sync_is_refreshed_and_the_page_is_retried(stream_name: str) -> None:
    url, query, next_url = _urls(stream_name)
    first_page = HttpRequest(url, query_params=query, headers={"Authorization": "Bearer token-1"})
    second_page_expired_token = HttpRequest(next_url, headers={"Authorization": "Bearer token-1"})
    second_page_fresh_token = HttpRequest(next_url, headers={"Authorization": "Bearer token-2"})

    with HttpMocker() as http_mocker:
        http_mocker.post(_TOKEN_REQUEST, [_token_response("token-1"), _token_response("token-2")])
        http_mocker.get(first_page, _page(1, next_url))
        http_mocker.get(second_page_expired_token, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(second_page_fresh_token, _page(2))

        output = _read(stream_name)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        http_mocker.assert_number_of_calls(_TOKEN_REQUEST, 2)
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page_expired_token, 1)
        http_mocker.assert_number_of_calls(second_page_fresh_token, 1)


def test_401_that_persists_after_one_token_refresh_fails_as_config_error() -> None:
    url, query, _ = _urls("mailings")
    rejected_with_first_token = HttpRequest(url, query_params=query, headers={"Authorization": "Bearer token-1"})
    rejected_with_second_token = HttpRequest(url, query_params=query, headers={"Authorization": "Bearer token-2"})

    with HttpMocker() as http_mocker:
        http_mocker.post(_TOKEN_REQUEST, [_token_response("token-1"), _token_response("token-2")])
        http_mocker.get(rejected_with_first_token, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(rejected_with_second_token, _EXPIRED_TOKEN_RESPONSE)

        output = _read("mailings")

        assert output.records == []
        # The stream error is followed by the sync-level summary error, which embeds the request URL.
        assert [error.trace.error.failure_type for error in output.errors] == [FailureType.config_error] * 2
        assert output.errors[0].trace.error.message == "Refreshed OAuth access token is rejected by the API."
        http_mocker.assert_number_of_calls(_TOKEN_REQUEST, 2)
        http_mocker.assert_number_of_calls(rejected_with_first_token, 1)
        http_mocker.assert_number_of_calls(rejected_with_second_token, 1)
