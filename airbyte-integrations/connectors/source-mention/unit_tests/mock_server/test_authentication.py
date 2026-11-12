# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_API_KEY = "test-mention-token"
_BASE_URL = "https://api.mention.net/api"
_ACCOUNT_ID = "acc_123"
_CONFIG: Dict[str, Any] = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_AUTH_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}


def _catalog(stream_name: str):
    return CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()


def _mock_account_me(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/accounts/me", headers=_AUTH_HEADERS),
        HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Acme"}}), status_code=200),
    )


class TestBearerAuthentication(TestCase):
    @HttpMocker()
    def test_account_me_sends_bearer_token(self, http_mocker: HttpMocker) -> None:
        """The Mention API only accepts `Authorization: Bearer <token>`; a bare token is rejected with 401."""
        _mock_account_me(http_mocker)

        output = read(get_source(config=_CONFIG), _CONFIG, _catalog("account_me"))

        assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]
        assert not output.errors


    @HttpMocker()
    def test_alert_pages_send_bearer_token(self, http_mocker: HttpMocker) -> None:
        """Every request of the alert stream (parent account_me and both alert pages) carries the Bearer token."""
        _mock_account_me(http_mocker)
        http_mocker.get(
            HttpRequest(
                url=f"{_BASE_URL}/accounts/{_ACCOUNT_ID}/alerts",
                query_params={"limit": "100", "cursor": "page2"},
                headers=_AUTH_HEADERS,
            ),
            HttpResponse(body=json.dumps({"alerts": [{"id": "alert_2"}], "_links": {}}), status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/accounts/{_ACCOUNT_ID}/alerts", query_params={"limit": "100"}, headers=_AUTH_HEADERS),
            HttpResponse(
                body=json.dumps({"alerts": [{"id": "alert_1"}], "_links": {"more": {"params": {"cursor": "page2"}}}}),
                status_code=200,
            ),
        )

        output = read(get_source(config=_CONFIG), _CONFIG, _catalog("alert"))

        assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2"]
        assert not output.errors

    @HttpMocker()
    def test_api_key_already_prefixed_with_bearer_is_not_double_prefixed(self, http_mocker: HttpMocker) -> None:
        """Configs where the user typed `Bearer <token>` as a workaround keep sending a single `Bearer` prefix."""
        _mock_account_me(http_mocker)
        config = {**_CONFIG, "api_key": f"Bearer {_API_KEY}"}

        output = read(get_source(config=config), config, _catalog("account_me"))

        assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]
        assert not output.errors
