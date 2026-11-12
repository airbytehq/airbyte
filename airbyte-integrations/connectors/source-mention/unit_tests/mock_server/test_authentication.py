# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


BASE_URL = "https://api.mention.net/api"
TOKEN = "test-mention-token"
MANIFEST_PATH = Path(__file__).parents[2] / "manifest.yaml"


def mock_endpoint(requests_mock: Mocker, path: str, payload: dict[str, Any], query: str = "", enforce_bearer: bool = True) -> None:
    def respond(request: Any, context: Any) -> dict[str, Any]:
        if enforce_bearer and request.headers.get("Authorization") != f"Bearer {TOKEN}":
            context.status_code = 401
            return {"error": "invalid_token", "error_description": "The access token provided is invalid."}
        return payload

    requests_mock.get(f"{BASE_URL}{path}{query}", json=respond, complete_qs=True)


@pytest.mark.parametrize(
    ("stream_name", "expected_ids"),
    [
        ("account_me", {"account-1"}),
        ("alert", {"alert-1", "alert-2"}),
        ("mention", {"mention-1", "mention-2", "mention-3", "mention-4"}),
    ],
)
def test_read_sends_bearer_token_to_parent_and_paginated_streams(requests_mock: Mocker, stream_name: str, expected_ids: set[str]) -> None:
    assert_read(requests_mock, stream_name, expected_ids, enforce_bearer=True)


@pytest.mark.parametrize(
    ("stream_name", "expected_ids"),
    [("alert", {"alert-1", "alert-2"}), ("mention", {"mention-1", "mention-2", "mention-3", "mention-4"})],
)
def test_read_stops_when_no_more_pages(requests_mock: Mocker, stream_name: str, expected_ids: set[str]) -> None:
    assert_read(requests_mock, stream_name, expected_ids, enforce_bearer=False)


def assert_read(requests_mock: Mocker, stream_name: str, expected_ids: set[str], enforce_bearer: bool) -> None:
    config = {"api_key": TOKEN, "stats_start_date": "2026-09-01T00:00:00Z"}
    mock_endpoint(requests_mock, "/accounts/me", {"account": {"id": "account-1"}}, enforce_bearer=enforce_bearer)
    mock_endpoint(
        requests_mock,
        "/accounts/account-1/alerts",
        {"alerts": [{"id": "alert-1"}], "_links": {"more": {"params": {"cursor": "alerts-next"}}}},
        "?limit=100",
        enforce_bearer=enforce_bearer,
    )
    mock_endpoint(
        requests_mock,
        "/accounts/account-1/alerts",
        {"alerts": [{"id": "alert-2"}]},
        "?limit=100&cursor=alerts-next",
        enforce_bearer=enforce_bearer,
    )
    for index, alert_id in enumerate(("alert-1", "alert-2")):
        path = f"/accounts/account-1/alerts/{alert_id}/mentions"
        mock_endpoint(
            requests_mock,
            path,
            {"mentions": [{"id": f"mention-{index * 2 + 1}"}], "_links": {"more": {"params": {"cursor": "mentions-next"}}}},
            "?limit=1000",
            enforce_bearer=enforce_bearer,
        )
        mock_endpoint(
            requests_mock,
            path,
            {"mentions": [{"id": f"mention-{index * 2 + 2}"}]},
            "?limit=1000&cursor=mentions-next",
            enforce_bearer=enforce_bearer,
        )

    source = YamlDeclarativeSource(str(MANIFEST_PATH), config=config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(source, config, catalog)

    assert not output.errors
    assert len(output.records) == len(expected_ids)
    assert {record.record.data["id"] for record in output.records if record.record is not None} == expected_ids
    expected_requests = {("/api/accounts/me", "")}
    if stream_name != "account_me":
        expected_requests.update(
            {
                ("/api/accounts/account-1/alerts", "limit=100"),
                ("/api/accounts/account-1/alerts", "cursor=alerts-next&limit=100"),
            }
        )
    if stream_name == "mention":
        expected_requests.update(
            (f"/api/accounts/account-1/alerts/{alert_id}/mentions", query)
            for alert_id in ("alert-1", "alert-2")
            for query in ("limit=1000", "cursor=mentions-next&limit=1000")
        )
    assert {(request.path, "&".join(sorted(request.query.split("&")))) for request in requests_mock.request_history} == expected_requests
    for request in requests_mock.request_history:
        assert request.method == "GET"
        if enforce_bearer:
            assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert request.body is None
