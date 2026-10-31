# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.models.outcome import ExpectedOutcome


MANIFEST = Path(__file__).parents[1] / "manifest.yaml"
CONFIG = {"api_key": "test-mention-token", "stats_start_date": "2026-09-01T00:00:00Z", "stats_interval": "P1D"}
BASE_URL = "https://api.mention.net/api"


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.mark.parametrize("stream_name", ["account_me", "alert", "mention", "statistics"])
def test_streams_send_bearer_token(stream_name: str) -> None:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog)
    headers = {"Authorization": f"Bearer {CONFIG['api_key']}"}

    with requests_mock.Mocker() as http:
        http.get(
            requests_mock.ANY,
            status_code=401,
            json={"error": "invalid_token", "error_description": "The access token provided is invalid."},
        )
        http.get(f"{BASE_URL}/accounts/me", request_headers=headers, json={"account": {"id": "account-id"}})
        http.get(
            f"{BASE_URL}/accounts/account-id/alerts",
            request_headers=headers,
            json={"alerts": [{"id": "alert-id"}], "_links": {}},
        )
        http.get(
            f"{BASE_URL}/accounts/account-id/alerts/alert-id/mentions",
            request_headers=headers,
            json={"mentions": [{"id": "mention-id"}], "_links": {}},
        )
        http.get(
            f"{BASE_URL}/accounts/account-id/stats",
            request_headers=headers,
            json={"from": "2026-09-01T00:00:00.000000+00:00", "to": "2026-09-02T00:00:00.000000+00:00"},
        )
        output = read(source, CONFIG, catalog)

        assert not output.errors
        assert len(output.records) == 1
        assert output.records[0].record.stream == stream_name
        assert http.request_history
        assert all(request.headers["Authorization"] == headers["Authorization"] for request in http.request_history)


def test_invalid_token_remains_an_error() -> None:
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog)

    with requests_mock.Mocker() as http:
        request = http.get(
            f"{BASE_URL}/accounts/me",
            request_headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
            status_code=401,
            json={"error": "invalid_token", "error_description": "The access token provided is invalid."},
        )
        output = read(source, CONFIG, catalog, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

    assert request.called
    assert not output.records
    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert "invalid_token" in output.errors[0].trace.error.internal_message
