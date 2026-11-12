# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source
from .config import API_KEY, ConfigBuilder


BASE_URL = "https://api.mention.net/api"
AUTH_HEADERS = {"Authorization": f"Bearer {API_KEY}"}
ACCOUNT_ID = "acc-123"


def _read(stream_name: str):
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


class TestBearerAuthentication(TestCase):
    """The Mention API only accepts `Authorization: Bearer <token>`; a bare token is rejected with 401."""

    @HttpMocker()
    def test_account_me_sends_bearer_token(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(url=f"{BASE_URL}/accounts/me", headers=AUTH_HEADERS),
            HttpResponse(body=json.dumps({"account": {"id": ACCOUNT_ID, "name": "Acme"}}), status_code=200),
        )

        output = _read("account_me")

        assert [record.record.data["id"] for record in output.records] == [ACCOUNT_ID]

    @HttpMocker()
    def test_alert_sends_bearer_token_to_parent_and_child_requests(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(url=f"{BASE_URL}/accounts/me", headers=AUTH_HEADERS),
            HttpResponse(body=json.dumps({"account": {"id": ACCOUNT_ID}}), status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{BASE_URL}/accounts/{ACCOUNT_ID}/alerts", query_params={"limit": "100"}, headers=AUTH_HEADERS),
            HttpResponse(body=json.dumps({"alerts": [{"id": 1}, {"id": 2}], "_links": {}}), status_code=200),
        )

        output = _read("alert")

        assert sorted(record.record.data["id"] for record in output.records) == [1, 2]
