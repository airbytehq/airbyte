# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for `source-mention` authentication.

Mention only accepts the access token as `Authorization: Bearer <token>`; a bare
token in the header is rejected with `401 invalid_token`. These tests mock the API
so that only requests carrying the Bearer header are answered.
"""

import json
from typing import Any, Dict, List, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder


_API_KEY = "my-mention-token"
_URL_BASE = "https://api.mention.net/api"
_ACCOUNT_ID = "acc-1"


def _request(path: str, query_params: Optional[Dict[str, Any]] = None) -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}{path}",
        query_params=query_params,
        headers={"Authorization": f"Bearer {_API_KEY}"},
    )


def _alerts_page(ids: List[str], next_cursor: Optional[str] = None) -> HttpResponse:
    body: Dict[str, Any] = {"alerts": [{"id": alert_id, "name": f"alert {alert_id}"} for alert_id in ids], "_links": {}}
    if next_cursor is not None:
        body["_links"]["more"] = {"href": "/more", "params": {"cursor": next_cursor}}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().with_api_key(_API_KEY).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def test_read_sends_api_key_as_bearer_token_on_every_request() -> None:
    """The parent request and both pages of the `alert` stream carry `Authorization: Bearer <api_key>`."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/accounts/me"),
            HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Acme"}}), status_code=200),
        )
        http_mocker.get(
            _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"}),
            _alerts_page(["alert-1", "alert-2"], next_cursor="page-2"),
        )
        http_mocker.get(
            _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100", "cursor": "page-2"}),
            _alerts_page(["alert-3"]),
        )

        output = _read("alert")

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["alert-1", "alert-2", "alert-3"]
