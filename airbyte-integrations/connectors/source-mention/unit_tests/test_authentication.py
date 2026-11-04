# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

CONFIG = {"api_key": "test-api-key", "stats_start_date": "2026-09-01T00:00:00Z"}
BASE_URL = "https://api.mention.net/api"


@pytest.mark.parametrize(
    "stream_name,record_id",
    [
        pytest.param("account_me", "account-id", id="account_me"),
        pytest.param("alert", "alert-id", id="alert"),
        pytest.param("mention", "mention-id", id="mention"),
    ],
)
def test_reads_authenticate_with_bearer_token(
    manifest_path: Path, stream_name: str, record_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG, catalog=catalog)

    with requests_mock.Mocker() as http:
        http.get(f"{BASE_URL}/accounts/me", json={"account": {"id": "account-id"}})
        http.get(
            f"{BASE_URL}/accounts/account-id/alerts",
            json={"alerts": [{"id": "alert-id"}], "_links": {}},
        )
        http.get(
            f"{BASE_URL}/accounts/account-id/alerts/alert-id/mentions",
            json={"mentions": [{"id": "mention-id"}], "_links": {}},
        )
        output = read(source, CONFIG, catalog)

    assert http.request_history
    for request in http.request_history:
        assert request.headers["Authorization"] == "Bearer test-api-key"
    assert not output.errors
    assert [message.record.data["id"] for message in output.records] == [record_id]


def test_check_authenticates_parent_and_alert(manifest_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG)
    with requests_mock.Mocker() as http:
        http.get(f"{BASE_URL}/accounts/me", json={"account": {"id": "account-id"}})
        http.get(f"{BASE_URL}/accounts/account-id/alerts", json={"alerts": [{"id": "alert-id"}], "_links": {}})
        result = source.check(logging.getLogger(), CONFIG)

    assert result.status.value == "SUCCEEDED"
    assert {request.path for request in http.request_history} == {"/api/accounts/me", "/api/accounts/account-id/alerts"}
    assert all(request.headers["Authorization"] == "Bearer test-api-key" for request in http.request_history)


def test_invalid_token_fails_instead_of_succeeding_with_empty_records(
    manifest_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG, catalog=catalog)
    with requests_mock.Mocker() as http:
        http.get(
            f"{BASE_URL}/accounts/me",
            status_code=401,
            json={"error": "invalid_token", "error_description": "The access token provided is invalid."},
        )
        output = read(source, CONFIG, catalog)

    assert http.last_request.headers["Authorization"] == "Bearer test-api-key"
    assert output.errors
    assert not output.records
