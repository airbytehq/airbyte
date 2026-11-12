# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for how `source-mention` authenticates against the Mention API.

Mention only accepts `Authorization: Bearer <access token>`; any other value is rejected with
`401 invalid_token`. Every stream shares one requester, so the header is checked along the
`account_me` -> `alert` -> `mention` chain, which covers the parent requests as well as the
requests of more than one partition.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder


_API_KEY = "mention-access-token"
_URL_BASE = "https://api.mention.net/api"
_ACCOUNT_ID = "account-1"
# Mention list responses carry `_links`; the last page has no `more` link, which stops pagination.
_LAST_PAGE_LINKS: Dict[str, Any] = {"pull": {"href": "/pull", "params": {"since_id": "1"}}}


def _request(path: str, query_params: Optional[Dict[str, Any]] = None) -> HttpRequest:
    """A request that only matches when it carries the bearer token Mention expects."""
    return HttpRequest(
        url=f"{_URL_BASE}{path}",
        query_params=query_params,
        headers={"Authorization": f"Bearer {_API_KEY}"},
    )


def _response(body: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().with_api_key(_API_KEY).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def _record_ids(output: EntrypointOutput) -> List[str]:
    return [record.record.data["id"] for record in output.records]


def _given_account_and_alerts(http_mocker: HttpMocker, alert_ids: List[str]) -> None:
    http_mocker.get(_request("/accounts/me"), _response({"account": {"id": _ACCOUNT_ID}}))
    http_mocker.get(
        _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"}),
        _response({"alerts": [{"id": alert_id} for alert_id in alert_ids], "_links": _LAST_PAGE_LINKS}),
    )


class TestAuthentication(TestCase):
    @HttpMocker()
    def test_alert_read_sends_bearer_token_and_emits_alerts(self, http_mocker: HttpMocker):
        _given_account_and_alerts(http_mocker, ["alert-1", "alert-2"])

        output = _read("alert")

        assert _record_ids(output) == ["alert-1", "alert-2"]
        assert output.errors == []

    @HttpMocker()
    def test_mention_read_sends_bearer_token_for_every_alert_partition(self, http_mocker: HttpMocker):
        _given_account_and_alerts(http_mocker, ["alert-1", "alert-2"])
        for alert_id, mention_id in (("alert-1", "mention-1"), ("alert-2", "mention-2")):
            http_mocker.get(
                _request(f"/accounts/{_ACCOUNT_ID}/alerts/{alert_id}/mentions", {"limit": "1000"}),
                _response({"mentions": [{"id": mention_id}], "_links": _LAST_PAGE_LINKS}),
            )

        output = _read("mention")

        # Partitions are read concurrently, so the order of the mentions is not deterministic.
        assert sorted(_record_ids(output)) == ["mention-1", "mention-2"]
        assert output.errors == []
