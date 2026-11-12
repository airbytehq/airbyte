# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import get_source  # noqa: E402

from .config import ConfigBuilder  # noqa: E402


_API = "https://api.mention.net/api"
_ACCESS_TOKEN = "test-access-token"
# The Mention API only accepts `Authorization: Bearer <access token>`. HttpMocker only answers
# requests carrying exactly these headers, so a request with any other Authorization value has
# no match and fails the read, the same way the real API answers it with 401 `invalid_token`.
_BEARER_HEADERS = {"Authorization": f"Bearer {_ACCESS_TOKEN}"}


@pytest.mark.parametrize(
    "configured_api_key",
    [
        pytest.param(_ACCESS_TOKEN, id="bare_access_token"),
        pytest.param(f"Bearer {_ACCESS_TOKEN}", id="token_already_prefixed_with_bearer"),
    ],
)
def test_read_sends_access_token_as_bearer_on_every_request(configured_api_key: str) -> None:
    """`alert` reads `/accounts/me` and then two pages of alerts; all three requests must carry the Bearer token."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{_API}/accounts/me", headers=_BEARER_HEADERS),
            HttpResponse(body='{"account": {"id": "acc_1", "name": "Acme"}}', status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{_API}/accounts/acc_1/alerts", query_params={"limit": "100"}, headers=_BEARER_HEADERS),
            HttpResponse(
                body='{"alerts": [{"id": "alert_1"}], "_links": {"more": {"params": {"cursor": "page-2"}}}}',
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{_API}/accounts/acc_1/alerts",
                query_params={"limit": "100", "cursor": "page-2"},
                headers=_BEARER_HEADERS,
            ),
            HttpResponse(body='{"alerts": [{"id": "alert_2"}], "_links": {}}', status_code=200),
        )

        config = ConfigBuilder().with_api_key(configured_api_key).build()
        catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=False)

        assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2"]
        assert output.errors == []
