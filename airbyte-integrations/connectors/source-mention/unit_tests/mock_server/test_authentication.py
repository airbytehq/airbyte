# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import _YAML_FILE_PATH

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


API = "https://api.mention.net/api"
TOKEN = "mention-test-token"
ACCOUNT = {"id": "123_abc", "name": "Acme"}
ALERTS = [{"id": 1, "name": "brand"}, {"id": 2, "name": "competitor"}]


@pytest.mark.parametrize(
    "api_key",
    [
        pytest.param(TOKEN, id="raw_token"),
        pytest.param(f"Bearer {TOKEN}", id="token_already_prefixed"),
    ],
)
def test_read_sends_bearer_token_and_emits_account_alerts(api_key: str) -> None:
    config = {"api_key": api_key, "stats_start_date": "2026-09-01T00:00:00Z"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    account_request = HttpRequest(url=f"{API}/accounts/me", headers=headers)
    alerts_request = HttpRequest(
        url=f"{API}/accounts/{ACCOUNT['id']}/alerts",
        query_params={"limit": "100"},
        headers=headers,
    )
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).with_stream("alert", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=None)

    with HttpMocker() as http:
        http.get(account_request, HttpResponse(body=json.dumps({"account": ACCOUNT})))
        http.get(alerts_request, HttpResponse(body=json.dumps({"alerts": ALERTS, "_links": {}})))

        output = read(source, config, catalog)

        assert not output.errors
        assert [m.record.data["id"] for m in output.records if m.record.stream == "account_me"] == [ACCOUNT["id"]]
        assert [m.record.data["id"] for m in output.records if m.record.stream == "alert"] == [1, 2]
        http.assert_number_of_calls(alerts_request, 1)
