# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

from requests_mock import Mocker
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_read_authenticates_parent_and_paginated_alerts(manifest_path: Path, requests_mock: Mocker) -> None:
    config = {"api_key": "test-mention-token", "stats_start_date": "2026-09-01T00:00:00Z"}
    authorization = f"Bearer {config['api_key']}"

    def account_response(request: _RequestObjectProxy, context: _Context) -> dict:
        if request.headers.get("Authorization") != authorization:
            context.status_code = 401
            return {"error": "invalid_token", "error_description": "The access token provided is invalid."}
        return {"account": {"id": "account-1", "name": "Test account"}}

    requests_mock.get("https://api.mention.net/api/accounts/me", json=account_response, complete_qs=True)
    requests_mock.get(
        "https://api.mention.net/api/accounts/account-1/alerts?limit=100",
        request_headers={"Authorization": authorization},
        json={
            "alerts": [{"id": "alert-1", "name": "First alert"}],
            "_links": {"more": {"params": {"cursor": "next-page"}}},
        },
        complete_qs=True,
    )
    requests_mock.get(
        "https://api.mention.net/api/accounts/account-1/alerts?limit=100&cursor=next-page",
        request_headers={"Authorization": authorization},
        json={"alerts": [{"id": "alert-2", "name": "Second alert"}], "_links": {"more": None}},
        complete_qs=True,
    )

    catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config, catalog=catalog)
    output = read(source, config=config, catalog=catalog)

    assert requests_mock.request_history[0].headers["Authorization"] == authorization
    assert len(output.records) == 2
    assert {message.record.data["id"] for message in output.records} == {"alert-1", "alert-2"}
    assert not output.errors
    assert [(request.method, request.path, request.qs) for request in requests_mock.request_history] == [
        ("GET", "/api/accounts/me", {}),
        ("GET", "/api/accounts/account-1/alerts", {"limit": ["100"]}),
        ("GET", "/api/accounts/account-1/alerts", {"limit": ["100"], "cursor": ["next-page"]}),
    ]
    assert all(request.headers["Authorization"] == authorization for request in requests_mock.request_history)
    assert all(request.body is None for request in requests_mock.request_history)
