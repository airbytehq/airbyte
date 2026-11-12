# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for how `source-mention` authenticates.

The Mention API only accepts `Authorization: Bearer <access token>`; any other
header value is answered with `401 invalid_token`. Every stream shares the same
requester, so the tests read `alert` (a substream of `account_me`, paginated) and
pin the header on the parent request and on each page of the child request.
"""

import json
from typing import Any, Dict, List, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_API_KEY = "test-access-token"
_ACCOUNT_ID = "acc_1"
_BASE_URL = "https://api.mention.net/api"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_INVALID_TOKEN_BODY = '{"error":"invalid_token","error_description":"The access token provided is invalid."}'


def _request(path: str, query_params: Optional[Dict[str, Any]] = None) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}{path}",
        query_params=query_params,
        headers={"Authorization": f"Bearer {_API_KEY}"},
    )


def _alerts_page(ids: List[str], next_cursor: Optional[str] = None) -> HttpResponse:
    body: Dict[str, Any] = {"alerts": [{"id": alert_id, "name": f"alert {alert_id}"} for alert_id in ids]}
    # Mention always returns `_links`; `more` is only present while there is another page.
    body["_links"] = {"pull": {"href": f"/api/accounts/{_ACCOUNT_ID}/alerts"}}
    if next_cursor:
        body["_links"]["more"] = {"params": {"cursor": next_cursor}}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read_alert() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog, expecting_exception=False)


def test_read_sends_the_api_key_as_a_bearer_token_on_every_request() -> None:
    with HttpMocker() as http_mocker:
        # Mention rejects any request that is not `Authorization: Bearer <token>`. These catch-alls are
        # registered first so the exact Bearer matchers below take precedence when they match.
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/accounts/me", query_params=ANY_QUERY_PARAMS),
            HttpResponse(body=_INVALID_TOKEN_BODY, status_code=401),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/accounts/{_ACCOUNT_ID}/alerts", query_params=ANY_QUERY_PARAMS),
            HttpResponse(body=_INVALID_TOKEN_BODY, status_code=401),
        )
        http_mocker.get(
            _request("/accounts/me"),
            HttpResponse(body='{"account": {"id": "%s", "name": "Acme"}}' % _ACCOUNT_ID, status_code=200),
        )
        http_mocker.get(
            _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"}),
            _alerts_page(["alert_1", "alert_2"], next_cursor="page-2"),
        )
        http_mocker.get(
            _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100", "cursor": "page-2"}),
            _alerts_page(["alert_3"]),
        )

        output = _read_alert()

    assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2", "alert_3"]
    assert output.errors == []
