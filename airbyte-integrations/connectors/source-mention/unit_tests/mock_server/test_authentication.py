# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mention authenticates with an OAuth-style bearer token: `Authorization: Bearer <token>`.
A raw token without the `Bearer` prefix is answered with 401 `invalid_token`.
API reference: https://dev.mention.com/
"""

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_API_KEY = "mention-access-token"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_AUTH_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}
_BASE_URL = "https://api.mention.net/api"
_ACCOUNT_ID = "1234567_abcdef"


def _account_me_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Acme"}}), status_code=200)


def _alerts_response() -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"alerts": [{"id": 101, "name": "Brand"}, {"id": 102, "name": "Competitor"}], "_links": {}}),
        status_code=200,
    )


class AuthenticationTest(TestCase):
    @HttpMocker()
    def test_account_me_sends_bearer_token(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/accounts/me", headers=_AUTH_HEADERS), _account_me_response())

        catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]

    @HttpMocker()
    def test_alert_parent_and_child_requests_send_bearer_token(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/accounts/me", headers=_AUTH_HEADERS), _account_me_response())
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/accounts/{_ACCOUNT_ID}/alerts", query_params={"limit": "100"}, headers=_AUTH_HEADERS),
            _alerts_response(),
        )

        catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [101, 102]
