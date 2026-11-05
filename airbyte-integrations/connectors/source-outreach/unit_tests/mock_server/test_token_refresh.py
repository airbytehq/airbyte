# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for OAuth token handling during long syncs.

Outreach access tokens expire after two hours and every refresh returns a new refresh
token that replaces the previous one. A long sync must therefore persist the rotated
refresh token, and must refresh the access token and retry when the API answers
`401 expiredAccessToken` instead of failing the sync.
"""

import io
import json
from contextlib import redirect_stdout
from typing import Any, Dict, List, Mapping, Tuple
from unittest import TestCase
from urllib.parse import urlencode

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import CLIENT_ID, CLIENT_SECRET, INITIAL_REFRESH_TOKEN, ConfigBuilder


_NOW = "2024-06-01T00:00:00Z"
_TOKEN_URL = "https://api.outreach.io/oauth/token"
_CALLS_URL = "https://api.outreach.io/api/v2/calls"
_CALLS_QUERY = {
    "count": "false",
    "sort": "updatedAt",
    "page[size]": "1000",
    "newFilterSyntax": "true",
    "filter[updatedAt][gte]": "2024-01-01T00:00:00.000Z",
}
_PAGE_2_CURSOR = "cursor-page-2"
_EXPIRED_ACCESS_TOKEN = {
    "errors": [
        {
            "id": "expiredAccessToken",
            "title": "Expired Access Token",
            "detail": "Please get a new access token and try again.",
        }
    ]
}


def _token_request(refresh_token: str) -> HttpRequest:
    body = urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
    )
    return HttpRequest(url=_TOKEN_URL, body=body)


def _token_response(access_token: str, refresh_token: str) -> HttpResponse:
    body = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 7200,
        "refresh_token": refresh_token,
        "scope": "calls.read",
        "created_at": 1717200000,
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


def _calls_request(access_token: str, page_after: str = "") -> HttpRequest:
    query = dict(_CALLS_QUERY)
    if page_after:
        query["page[after]"] = page_after
    return HttpRequest(url=_CALLS_URL, query_params=query, headers={"Authorization": f"Bearer {access_token}"})


def _call(call_id: int, updated_at: str) -> Dict[str, Any]:
    return {"type": "call", "id": call_id, "attributes": {"updatedAt": updated_at}, "relationships": {}}


def _calls_response(calls: List[Dict[str, Any]], next_page_after: str = "") -> HttpResponse:
    links: Dict[str, Any] = {}
    if next_page_after:
        links["next"] = f"{_CALLS_URL}?{urlencode({**_CALLS_QUERY, 'page[after]': next_page_after})}"
    return HttpResponse(body=json.dumps({"data": calls, "links": links}), status_code=200)


def _read(config: Mapping[str, Any], expecting_exception: bool = False) -> Tuple[EntrypointOutput, List[Mapping[str, Any]]]:
    """Run a read of `calls` and return its output plus the configs emitted as CONNECTOR_CONFIG control messages.

    The CDK prints CONNECTOR_CONFIG control messages straight to stdout, so stdout is captured here.
    """
    catalog = CatalogBuilder().with_stream("calls", SyncMode.full_refresh).build()
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        output = read(get_source(config=config), config=config, catalog=catalog, expecting_exception=expecting_exception)
    emitted_configs = []
    for line in stdout.getvalue().splitlines():
        if not line.startswith("{"):
            continue
        message = json.loads(line)
        if message.get("type") == "CONTROL" and message["control"]["type"] == "CONNECTOR_CONFIG":
            emitted_configs.append(message["control"]["connectorConfig"]["config"])
    return output, emitted_configs


@freezegun.freeze_time(_NOW)
class TestTokenRefresh(TestCase):
    @HttpMocker()
    def test_rotated_refresh_token_is_persisted_to_config(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(_token_request(INITIAL_REFRESH_TOKEN), _token_response("access-token-1", "refresh-token-2"))
        http_mocker.get(_calls_request("access-token-1"), _calls_response([_call(1, "2024-05-01T00:00:00.000Z")]))

        output, emitted = _read(ConfigBuilder().build())

        assert [record.record.data["id"] for record in output.records] == [1]
        assert emitted, "the rotated refresh token was not emitted as a connector config control message"
        assert emitted[-1]["refresh_token"] == "refresh-token-2"
        assert emitted[-1]["access_token"] == "access-token-1"

    @HttpMocker()
    def test_expired_access_token_mid_sync_is_refreshed_with_rotated_refresh_token(self, http_mocker: HttpMocker) -> None:
        initial_token_request = _token_request(INITIAL_REFRESH_TOKEN)
        rotated_token_request = _token_request("refresh-token-2")
        http_mocker.post(initial_token_request, _token_response("access-token-1", "refresh-token-2"))
        http_mocker.post(rotated_token_request, _token_response("access-token-2", "refresh-token-3"))
        http_mocker.get(
            _calls_request("access-token-1"),
            _calls_response([_call(1, "2024-05-01T00:00:00.000Z")], next_page_after=_PAGE_2_CURSOR),
        )
        http_mocker.get(
            _calls_request("access-token-1", _PAGE_2_CURSOR),
            HttpResponse(body=json.dumps(_EXPIRED_ACCESS_TOKEN), status_code=401),
        )
        http_mocker.get(
            _calls_request("access-token-2", _PAGE_2_CURSOR),
            _calls_response([_call(2, "2024-05-02T00:00:00.000Z")]),
        )

        output, emitted = _read(ConfigBuilder().build())

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        http_mocker.assert_number_of_calls(initial_token_request, 1)
        http_mocker.assert_number_of_calls(rotated_token_request, 1)
        assert [config["refresh_token"] for config in emitted] == ["refresh-token-2", "refresh-token-3"]
        assert emitted[-1]["access_token"] == "access-token-2"

    @HttpMocker()
    def test_unauthorized_other_than_expired_token_fails_as_config_error(self, http_mocker: HttpMocker) -> None:
        token_request = _token_request(INITIAL_REFRESH_TOKEN)
        http_mocker.post(token_request, _token_response("access-token-1", "refresh-token-2"))
        http_mocker.get(
            _calls_request("access-token-1"),
            HttpResponse(
                body=json.dumps({"errors": [{"id": "unauthorizedOauthScope", "title": "Unauthorized OAuth Scope"}]}),
                status_code=401,
            ),
        )

        output, _ = _read(ConfigBuilder().build(), expecting_exception=True)

        assert output.records == []
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
        http_mocker.assert_number_of_calls(token_request, 1)
