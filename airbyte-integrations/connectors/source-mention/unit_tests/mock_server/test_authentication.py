# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test-access-token"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_URL_BASE = "https://api.mention.net/api"
_BEARER_HEADER = {"Authorization": f"Bearer {_API_KEY}"}
_ACCOUNT_ID = "acc-1"


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def _given_account_me(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/accounts/me", headers=_BEARER_HEADER),
        HttpResponse(json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Example account"}}), 200),
    )


def test_account_me_sends_api_key_as_bearer_token() -> None:
    with HttpMocker() as http_mocker:
        _given_account_me(http_mocker)
        output = _read("account_me")

    assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]
    assert not output.errors


def test_alert_substream_sends_api_key_as_bearer_token_on_parent_and_child() -> None:
    with HttpMocker() as http_mocker:
        _given_account_me(http_mocker)
        http_mocker.get(
            HttpRequest(url=f"{_URL_BASE}/accounts/{_ACCOUNT_ID}/alerts", query_params={"limit": "100"}, headers=_BEARER_HEADER),
            HttpResponse(json.dumps({"alerts": [{"id": "alert-1"}, {"id": "alert-2"}], "_links": {}}), 200),
        )
        output = _read("alert")

    assert [record.record.data["id"] for record in output.records] == ["alert-1", "alert-2"]
    assert not output.errors
