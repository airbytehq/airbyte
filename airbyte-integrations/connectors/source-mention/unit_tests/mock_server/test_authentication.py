# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test-api-key", "stats_start_date": "2026-11-01T00:00:00Z"}
HEADERS = {"Authorization": "Bearer test-api-key"}


@pytest.mark.parametrize("stream_name", ["account_me", "alert"])
@pytest.mark.parametrize("empty", [False, True])
def test_read_with_bearer_token(http_mocker: HttpMocker, stream_name: str, empty: bool) -> None:
    account_request = HttpRequest("https://api.mention.net/api/accounts/me", headers=HEADERS)
    account = {"id": "account-123"}
    http_mocker.get(account_request, HttpResponse(json.dumps({"account": account if stream_name == "alert" or not empty else []})))
    expected_ids = [] if empty else ["account-123"]
    if stream_name == "alert":
        alert_request = HttpRequest(
            "https://api.mention.net/api/accounts/account-123/alerts", headers=HEADERS, query_params={"limit": "100"}
        )
        alerts = [] if empty else [{"id": "alert-456"}, {"id": "alert-789"}]
        http_mocker.get(alert_request, HttpResponse(json.dumps({"alerts": alerts, "_links": {}})))
        expected_ids = [alert["id"] for alert in alerts]

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(CONFIG), config=CONFIG, catalog=catalog)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == expected_ids
    http_mocker.assert_number_of_calls(account_request, 1)
    if stream_name == "alert":
        http_mocker.assert_number_of_calls(alert_request, 1)


def test_invalid_token(http_mocker: HttpMocker) -> None:
    request = HttpRequest("https://api.mention.net/api/accounts/me", headers=HEADERS)
    http_mocker.get(request, HttpResponse(json.dumps({"error": "invalid_token"}), status_code=401))
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()

    output = read(get_source(CONFIG), config=CONFIG, catalog=catalog, expecting_exception=True)

    assert output.records == []
    assert output.errors
    http_mocker.assert_number_of_calls(request, 1)
