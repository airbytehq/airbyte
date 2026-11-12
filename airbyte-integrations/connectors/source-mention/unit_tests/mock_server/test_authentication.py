# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


@pytest.mark.parametrize("stream_name", ["account_me", "alert"])
@pytest.mark.parametrize("has_records", [True, False])
def test_read_with_bearer_token(stream_name: str, has_records: bool) -> None:
    config = {"api_key": "test-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}
    headers = {"Authorization": "Bearer test-api-key"}
    account = {"id": "account-1"}
    account_body = {"account": account if has_records or stream_name == "alert" else {}}
    with HttpMocker() as http:
        http.get(
            HttpRequest(url="https://api.mention.net/api/accounts/me", headers=headers),
            HttpResponse(json.dumps(account_body), 200),
        )
        if stream_name == "alert":
            http.get(
                HttpRequest(
                    url="https://api.mention.net/api/accounts/account-1/alerts",
                    headers=headers,
                    query_params={"limit": "100"},
                ),
                HttpResponse(
                    json.dumps({"alerts": [{"id": "alert-1"}, {"id": "alert-2"}] if has_records else [], "_links": {"more": None}}),
                    200,
                ),
            )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

    assert not output.errors
    expected_ids = (["account-1"] if stream_name == "account_me" else ["alert-1", "alert-2"]) if has_records else []
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids


def test_read_with_rejected_token() -> None:
    config = {"api_key": "invalid-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}
    with HttpMocker() as http:
        http.get(
            HttpRequest(
                url="https://api.mention.net/api/accounts/me",
                headers={"Authorization": "Bearer invalid-api-key"},
            ),
            HttpResponse(json.dumps({"error": "invalid_token"}), 401),
        )
        catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

    assert not output.records
    assert output.errors
    assert any("401" in log.log.message and "invalid_token" in log.log.message for log in output.logs)
