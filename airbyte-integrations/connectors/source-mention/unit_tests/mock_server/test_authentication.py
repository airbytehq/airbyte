# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for how `source-mention` authenticates against the Mention API.

The Mention API expects an OAuth-style bearer token: `Authorization: Bearer <api_key>`.
The mocks below only answer requests that carry that exact header, so a connector that
sends the raw key (`Authorization: <api_key>`) gets no records.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder


_API_BASE = "https://api.mention.net/api"
_API_KEY = "my-mention-token"
_AUTH_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}
_ACCOUNT_ID = "acc-1"
_ALERT_ID = 101


def _request(path: str, query_params: Dict[str, Any] = None) -> HttpRequest:
    return HttpRequest(url=f"{_API_BASE}{path}", query_params=query_params, headers=_AUTH_HEADERS)


def _json(body: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=200)


def _mock_account_me(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _request("/accounts/me"),
        _json({"account": {"id": _ACCOUNT_ID, "name": "Acme"}}),
    )


def _mock_alerts(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"}),
        _json({"alerts": [{"id": _ALERT_ID, "name": "Brand"}], "_links": {}}),
    )


def _mock_mentions(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _request(f"/accounts/{_ACCOUNT_ID}/alerts/{_ALERT_ID}/mentions", {"limit": "1000"}),
        _json({"mentions": [{"id": 9001, "title": "Acme in the news"}, {"id": 9002, "title": "Acme again"}], "_links": {}}),
    )


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().with_api_key(_API_KEY).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config, catalog)


def _record_ids(output: EntrypointOutput) -> List[Any]:
    return [record.record.data["id"] for record in output.records]


class TestBearerAuthentication(TestCase):
    @HttpMocker()
    def test_account_me_sends_bearer_token(self, http_mocker: HttpMocker) -> None:
        _mock_account_me(http_mocker)

        output = _read("account_me")

        assert _record_ids(output) == [_ACCOUNT_ID]
        assert not output.errors

    @HttpMocker()
    def test_alert_sends_bearer_token_to_parent_and_child(self, http_mocker: HttpMocker) -> None:
        _mock_account_me(http_mocker)
        _mock_alerts(http_mocker)

        output = _read("alert")

        assert _record_ids(output) == [_ALERT_ID]
        assert not output.errors

    @HttpMocker()
    def test_mention_sends_bearer_token_through_nested_partitions(self, http_mocker: HttpMocker) -> None:
        _mock_account_me(http_mocker)
        _mock_alerts(http_mocker)
        _mock_mentions(http_mocker)

        output = _read("mention")

        assert _record_ids(output) == [9001, 9002]
        assert not output.errors
