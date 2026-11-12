# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for how `source-mention` authenticates against the Mention API.

Mention expects `Authorization: Bearer <access token>` on every request. These
tests drive real reads through the manifest and only answer requests carrying
that header, so a regression in the auth header surfaces as a failed read.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.mention.net/api"
_TOKEN = "test-access-token"
_ACCOUNT_ID = "acc-1"


def _config(api_key: str) -> Dict[str, Any]:
    return {"api_key": api_key, "stats_start_date": "2026-09-01T00:00:00Z"}


def _request(path: str, query_params: Dict[str, Any] = None) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}{path}",
        query_params=query_params,
        headers={"Authorization": f"Bearer {_TOKEN}"},
    )


def _account_me_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Test Account"}}), status_code=200)


def _alerts_response(alert_ids: List[str]) -> HttpResponse:
    body = {"alerts": [{"id": alert_id, "name": f"Alert {alert_id}"} for alert_id in alert_ids], "_links": {}}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str, api_key: str) -> EntrypointOutput:
    config = _config(api_key)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config, catalog)


class TestAuthentication(TestCase):
    @HttpMocker()
    def test_account_me_sends_bearer_token(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request("/accounts/me"), _account_me_response())

        output = _read("account_me", _TOKEN)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]

    @HttpMocker()
    def test_alert_sends_bearer_token_on_parent_and_child_requests(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request("/accounts/me"), _account_me_response())
        http_mocker.get(
            _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"}),
            _alerts_response(["alert-1", "alert-2"]),
        )

        output = _read("alert", _TOKEN)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["alert-1", "alert-2"]

    @HttpMocker()
    def test_api_key_already_prefixed_with_bearer_is_not_double_prefixed(self, http_mocker: HttpMocker) -> None:
        """Users who worked around the missing prefix by pasting `Bearer <token>` keep working."""
        http_mocker.get(_request("/accounts/me"), _account_me_response())

        output = _read("account_me", f"Bearer {_TOKEN}")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]
