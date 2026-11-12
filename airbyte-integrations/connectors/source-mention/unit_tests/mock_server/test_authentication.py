# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_URL_BASE = "https://api.mention.net/api"
_TOKEN = "test_access_token"
_ACCOUNT_ID = "acc_1"


def _config(api_key: str) -> dict:
    return {"api_key": api_key, "stats_start_date": "2026-09-01T00:00:00Z"}


@pytest.mark.parametrize(
    "api_key",
    [
        pytest.param(_TOKEN, id="bare_token"),
        pytest.param(f"Bearer {_TOKEN}", id="token_already_prefixed_with_bearer"),
    ],
)
def test_alert_read_sends_bearer_token_on_every_request(api_key: str):
    """
    The Mention API only accepts `Authorization: Bearer <token>`. The mocks below only match
    that exact header, on the parent (`/accounts/me`) request and on both pages of `alert`.
    """
    auth_headers = {"Authorization": f"Bearer {_TOKEN}"}
    config = _config(api_key)

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{_URL_BASE}/accounts/me", headers=auth_headers),
            HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID}}), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{_URL_BASE}/accounts/{_ACCOUNT_ID}/alerts",
                query_params={"limit": "100"},
                headers=auth_headers,
            ),
            HttpResponse(
                body=json.dumps({"alerts": [{"id": "alert_1"}], "_links": {"more": {"params": {"cursor": "page_2"}}}}),
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{_URL_BASE}/accounts/{_ACCOUNT_ID}/alerts",
                query_params={"limit": "100", "cursor": "page_2"},
                headers=auth_headers,
            ),
            HttpResponse(body=json.dumps({"alerts": [{"id": "alert_2"}], "_links": {}}), status_code=200),
        )

        catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
        output = read(get_source(config=config), config=config, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2"]
    assert output.errors == []
