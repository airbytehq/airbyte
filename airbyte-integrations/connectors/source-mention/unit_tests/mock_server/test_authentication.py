# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_URL_BASE = "https://api.mention.net/api"
_ACCOUNT_ID = "acc_1"


def _authorized(path: str, query_params: dict | None = None) -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}{path}",
        query_params=query_params,
        headers={"Authorization": "Bearer test-token"},
    )


@pytest.mark.parametrize("api_key", ["test-token", "Bearer test-token"], ids=["raw_token", "token_with_bearer_prefix"])
def test_read_sends_bearer_authorization_header(http_mocker: HttpMocker, api_key: str) -> None:
    config = {"api_key": api_key, "stats_start_date": "2026-09-01T00:00:00Z"}
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).with_stream("alert", SyncMode.full_refresh).build()
    account_request = _authorized("/accounts/me")
    alerts_request = _authorized(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"})
    http_mocker.get(account_request, HttpResponse(body=f'{{"account": {{"id": "{_ACCOUNT_ID}", "name": "Acme"}}}}'))
    http_mocker.get(alerts_request, HttpResponse(body='{"alerts": [{"id": 11}, {"id": 12}], "_links": {}}'))

    output = read(get_source(config), config, catalog)

    assert output.errors == []
    assert sorted((m.record.stream, m.record.data["id"]) for m in output.records) == [
        ("account_me", _ACCOUNT_ID),
        ("alert", 11),
        ("alert", 12),
    ]
    http_mocker.assert_number_of_calls(alerts_request, 1)
