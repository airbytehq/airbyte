# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


TOKEN = "test-mention-token"
BASE_URL = "https://api.mention.net/api"


@pytest.mark.parametrize(
    ("stream_name", "expected_ids", "expected_requests"),
    [
        ("account_me", ["account-1"], [("/accounts/me", "")]),
        (
            "alert",
            ["alert-1", "alert-2"],
            [
                ("/accounts/me", ""),
                ("/accounts/account-1/alerts", "limit=100"),
                ("/accounts/account-1/alerts", "limit=100&cursor=next-alert"),
            ],
        ),
        (
            "mention",
            ["mention-1", "mention-2", "mention-3"],
            [
                ("/accounts/me", ""),
                ("/accounts/me", ""),
                ("/accounts/account-1/alerts", "limit=100"),
                ("/accounts/account-1/alerts", "limit=100&cursor=next-alert"),
                ("/accounts/account-1/alerts/alert-1/mentions", "limit=1000"),
                ("/accounts/account-1/alerts/alert-1/mentions", "limit=1000&cursor=next-mention"),
                ("/accounts/account-1/alerts/alert-2/mentions", "limit=1000"),
            ],
        ),
    ],
)
def test_read_sends_bearer_token_on_parent_and_paginated_requests(
    manifest_path: Path,
    requests_mock: requests_mock.Mocker,
    stream_name: str,
    expected_ids: list[str],
    expected_requests: list[tuple[str, str]],
) -> None:
    config = {"api_key": TOKEN, "stats_start_date": "2026-09-01T00:00:00Z"}
    responses = {
        ("/accounts/me", ""): {"account": {"id": "account-1"}},
        ("/accounts/account-1/alerts", ""): {
            "alerts": [{"id": "alert-1"}],
            "_links": {"more": {"params": {"cursor": "next-alert"}}},
        },
        ("/accounts/account-1/alerts", "next-alert"): {
            "alerts": [{"id": "alert-2"}],
            "_links": {"more": None},
        },
        ("/accounts/account-1/alerts/alert-1/mentions", ""): {
            "mentions": [{"id": "mention-1"}],
            "_links": {"more": {"params": {"cursor": "next-mention"}}},
        },
        ("/accounts/account-1/alerts/alert-1/mentions", "next-mention"): {
            "mentions": [{"id": "mention-2"}],
            "_links": {"more": None},
        },
        ("/accounts/account-1/alerts/alert-2/mentions", ""): {
            "mentions": [{"id": "mention-3"}],
            "_links": {"more": None},
        },
    }

    for (path, cursor), payload in responses.items():
        query = f"?cursor={cursor}" if cursor else ""
        requests_mock.get(
            f"{BASE_URL}{path}{query}",
            status_code=401,
            json={"error": "invalid_token", "error_description": "The access token provided is invalid."},
        )
        requests_mock.get(
            f"{BASE_URL}{path}{query}",
            request_headers={"Authorization": f"Bearer {TOKEN}"},
            json=payload,
        )

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config, catalog=catalog, state=[])
    output = read(source, config=config, catalog=catalog)

    assert [request.headers["Authorization"] for request in requests_mock.request_history] == [f"Bearer {TOKEN}"] * len(
        requests_mock.request_history
    )
    assert output.errors == []
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids
    assert len(output.records) == len(expected_ids)
    actual_requests = [
        (urlparse(request.url).path.removeprefix("/api"), parse_qs(urlparse(request.url).query))
        for request in requests_mock.request_history
    ]
    assert sorted(actual_requests, key=str) == sorted([(path, parse_qs(query)) for path, query in expected_requests], key=str)
