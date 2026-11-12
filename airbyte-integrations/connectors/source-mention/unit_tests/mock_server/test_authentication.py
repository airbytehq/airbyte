# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test_api_key"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_URL_BASE = "https://api.mention.net/api"
# The Mention API rejects any request whose Authorization header is not `Bearer <token>` with a 401 `invalid_token`.
_AUTH_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}


def test_read_alerts_sends_bearer_token_on_parent_and_every_page() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{_URL_BASE}/accounts/me", headers=_AUTH_HEADERS),
            HttpResponse(body='{"account": {"id": "acc_1", "name": "Acme"}}', status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{_URL_BASE}/accounts/acc_1/alerts", query_params={"limit": "100"}, headers=_AUTH_HEADERS),
            HttpResponse(
                body='{"alerts": [{"id": "alert_1"}], "_links": {"more": {"params": {"cursor": "page2"}}}}',
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{_URL_BASE}/accounts/acc_1/alerts",
                query_params={"limit": "100", "cursor": "page2"},
                headers=_AUTH_HEADERS,
            ),
            HttpResponse(
                body='{"alerts": [{"id": "alert_2"}], "_links": {"pull": {"params": {"since_id": "alert_2"}}}}',
                status_code=200,
            ),
        )

        catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2"]
        assert output.errors == []
