# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


BASE_URL = "https://api.mention.net/api"
TOKEN = "test-mention-token"
CONFIG = {"api_key": TOKEN, "stats_start_date": "2026-09-01T00:00:00Z"}


def _page(field: str, record_id: str, cursor: str | None = None) -> dict:
    return {
        field: [{"id": record_id}],
        "_links": {"more": {"params": {"cursor": cursor}} if cursor else None},
    }


@pytest.mark.parametrize(
    "stream_name,expected_ids",
    [
        ("account_me", ["account-1"]),
        ("alert", ["alert-1", "alert-2"]),
        ("mention", ["mention-1", "mention-2", "mention-3", "mention-4"]),
    ],
)
def test_read_sends_bearer_token_to_parent_and_paginated_streams(
    manifest_path: Path, requests_mock: Mocker, stream_name: str, expected_ids: list[str]
) -> None:
    def authorized(payload: dict):
        def respond(request, context):
            if request.headers.get("Authorization") != f"Bearer {TOKEN}":
                context.status_code = 401
                return {"error": "invalid_token", "error_description": "The access token provided is invalid."}
            return payload

        return respond

    requests_mock.get(f"{BASE_URL}/accounts/me", complete_qs=True, json=authorized({"account": {"id": "account-1"}}))
    alert_path = "/api/accounts/account-1/alerts"
    requests_mock.get(
        f"{BASE_URL}/accounts/account-1/alerts?limit=100",
        complete_qs=True,
        json=authorized(_page("alerts", "alert-1", "alert-page-2")),
    )
    requests_mock.get(
        f"{BASE_URL}/accounts/account-1/alerts?limit=100&cursor=alert-page-2",
        complete_qs=True,
        json=authorized(_page("alerts", "alert-2")),
    )
    for index, alert_id in enumerate(["alert-1", "alert-2"]):
        url = f"{BASE_URL}/accounts/account-1/alerts/{alert_id}/mentions"
        requests_mock.get(
            f"{url}?limit=1000",
            complete_qs=True,
            json=authorized(_page("mentions", f"mention-{index * 2 + 1}", "mention-page-2")),
        )
        requests_mock.get(
            f"{url}?limit=1000&cursor=mention-page-2",
            complete_qs=True,
            json=authorized(_page("mentions", f"mention-{index * 2 + 2}")),
        )

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG, catalog=catalog)
    output = read(source, CONFIG, catalog)

    assert requests_mock.request_history
    assert {request.headers.get("Authorization") for request in requests_mock.request_history} == {f"Bearer {TOKEN}"}
    assert not output.errors
    assert sorted(message.record.data["id"] for message in output.records) == expected_ids

    expected_requests = []
    if stream_name != "account_me":
        expected_requests.extend([(alert_path, {"limit": ["100"]}), (alert_path, {"limit": ["100"], "cursor": ["alert-page-2"]})])
    if stream_name == "mention":
        for alert_id in ["alert-1", "alert-2"]:
            path = f"{alert_path}/{alert_id}/mentions"
            expected_requests.extend([(path, {"limit": ["1000"]}), (path, {"limit": ["1000"], "cursor": ["mention-page-2"]})])
    actual_requests = [(urlsplit(request.url).path, parse_qs(urlsplit(request.url).query)) for request in requests_mock.request_history]
    account_requests = [request for request in actual_requests if request[0] == "/api/accounts/me"]
    # The two mention parent routers can race the shared account cache.
    assert len(account_requests) in ({1, 2} if stream_name == "mention" else {1})
    assert all(query == {} for _, query in account_requests)
    actual_requests = [request for request in actual_requests if request[0] != "/api/accounts/me"]
    # Concurrent partitions may interleave, but every page must be requested exactly once.
    request_key = lambda item: (item[0], item[1].get("cursor", []))
    assert sorted(actual_requests, key=request_key) == sorted(expected_requests, key=request_key)
