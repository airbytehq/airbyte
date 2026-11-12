# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test_api_key"
_URL_BASE = "https://api.mention.net/api"
_ACCOUNT_ID = "account_1"
# The Mention API only accepts the token as `Authorization: Bearer <token>`. HttpMocker leaves
# a request without exactly this header unmatched, which fails the read with no records.
_AUTH_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}


def _read(stream_name: str, api_key: str):
    config = {"api_key": api_key, "stats_start_date": "2026-09-01T00:00:00Z"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


@pytest.mark.parametrize(
    "configured_api_key",
    [
        pytest.param(_API_KEY, id="bare_token"),
        pytest.param(f"Bearer {_API_KEY}", id="token_already_prefixed_with_bearer"),
    ],
)
def test_alert_read_sends_bearer_token_on_parent_and_every_page(configured_api_key: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{_URL_BASE}/accounts/me", headers=_AUTH_HEADERS),
            HttpResponse(body=f'{{"account": {{"id": "{_ACCOUNT_ID}", "name": "Acme"}}}}', status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{_URL_BASE}/accounts/{_ACCOUNT_ID}/alerts",
                query_params={"limit": "100"},
                headers=_AUTH_HEADERS,
            ),
            HttpResponse(
                body='{"alerts": [{"id": "alert_1"}, {"id": "alert_2"}], "_links": {"more": {"params": {"cursor": "next_cursor"}}}}',
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{_URL_BASE}/accounts/{_ACCOUNT_ID}/alerts",
                query_params={"limit": "100", "cursor": "next_cursor"},
                headers=_AUTH_HEADERS,
            ),
            HttpResponse(body='{"alerts": [{"id": "alert_3"}], "_links": {}}', status_code=200),
        )

        output = _read("alert", configured_api_key)

    assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2", "alert_3"]
    assert output.errors == []
