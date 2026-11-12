# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source


_TOKEN_URL = "https://api.outreach.io/oauth/token"
_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2020-11-16T00:00:00Z",
}
_EXPIRED_TOKEN_RESPONSE = HttpResponse(
    body=json.dumps(
        {
            "id": "expiredAccessToken",
            "title": "Expired Access Token",
            "detail": "Please get a new access token and try again.",
        }
    ),
    status_code=401,
)


def _token_request() -> HttpRequest:
    return HttpRequest(
        _TOKEN_URL,
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )


def _token_response(access_token: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": access_token, "expires_in": 7200}), status_code=200)


def _stream_request(path: str, access_token: str, page_size: str = "100") -> HttpRequest:
    return HttpRequest(
        f"https://api.outreach.io/api/v2/{path}",
        query_params={
            "count": "false",
            "sort": "updatedAt",
            "page[size]": page_size,
            "newFilterSyntax": "true",
            "filter[updatedAt][gte]": "2020-11-16T00:00:00.000Z",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    state = StateBuilder().build()
    return read(build_source(config=_CONFIG, state=state), _CONFIG, catalog, state, expecting_exception=True)


@pytest.mark.parametrize(("stream_name", "page_size"), [("mailings", "100"), ("calls", "1000")])
def test_expired_access_token_mid_sync_is_refreshed_and_the_request_retried(stream_name: str, page_size: str) -> None:
    stale_request = _stream_request(stream_name, "stale-access-token", page_size)
    fresh_request = _stream_request(stream_name, "fresh-access-token", page_size)
    with HttpMocker() as http_mocker:
        token_request = _token_request()
        http_mocker.post(token_request, [_token_response("stale-access-token"), _token_response("fresh-access-token")])
        http_mocker.get(stale_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(
            fresh_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {"id": 1, "type": "mailing", "attributes": {"updatedAt": "2021-01-01T00:00:00.000Z"}},
                            {"id": 2, "type": "mailing", "attributes": {"updatedAt": "2021-01-02T00:00:00.000Z"}},
                        ]
                    }
                ),
                status_code=200,
            ),
        )
        output = _read(stream_name)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(stale_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)


def test_401_that_persists_after_a_token_refresh_fails_as_config_error_without_refreshing_again() -> None:
    stale_request = _stream_request("mailings", "stale-access-token")
    fresh_request = _stream_request("mailings", "fresh-access-token")
    with HttpMocker() as http_mocker:
        token_request = _token_request()
        http_mocker.post(token_request, [_token_response("stale-access-token"), _token_response("fresh-access-token")])
        http_mocker.get(stale_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(fresh_request, _EXPIRED_TOKEN_RESPONSE)
        output = _read("mailings")

        assert output.records == []
        # The stream-level failure is reported first, followed by the sync-level summary error.
        stream_error = output.errors[0].trace.error
        assert stream_error.failure_type == FailureType.config_error
        assert stream_error.message == "Refreshed OAuth access token is rejected by the API."
        assert "Outreach rejected the access token as expired or invalid." in stream_error.internal_message
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(stale_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)
