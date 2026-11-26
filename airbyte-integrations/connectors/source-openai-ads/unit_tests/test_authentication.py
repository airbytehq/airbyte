# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from urllib.parse import parse_qs

import pytest
from freezegun import freeze_time
from jsonschema import Draft7Validator
from requests_mock import ANY, Mocker

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_URL = "https://api.ads.openai.com/v1"
_TOKEN_URL = "https://auth.openai.com/api/accounts/oauth/token"
_UNEXPECTED_REQUEST = {"status_code": 400, "json": {"error": {"message": "The test did not expect this request."}}}
_DATES = {"start_date": "2026-09-01", "end_date": "2026-09-14"}
_LEGACY_CONFIG = {"api_key": "test-key", **_DATES}
_API_KEY_CONFIG = {"credentials": {"auth_type": "API Key", "api_key": "test-key"}, **_DATES}
_OAUTH_CONFIG = {
    "credentials": {
        "auth_type": "OAuth2.0",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-1",
        "ad_account_id": "adacct_123",
    },
    **_DATES,
}
_ACCOUNT = {"id": "adacct_123", "name": "Acme"}


@pytest.fixture(autouse=True)
def isolated_http(requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    requests_mock.register_uri(ANY, ANY, **_UNEXPECTED_REQUEST)


def _source(config: dict) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH), catalog=CatalogBuilder().build(), config=config, state=StateBuilder().build()
    )


def _mock_token(requests_mock: Mocker, **extra: str) -> None:
    requests_mock.post(_TOKEN_URL, json={"access_token": "access-1", "expires_in": 3600, "token_type": "Bearer", **extra})


def _api_requests(requests_mock: Mocker) -> list:
    return [request for request in requests_mock.request_history if request.url.startswith(_URL)]


def test_spec_accepts_oauth_and_api_key_credentials() -> None:
    spec = _source(_API_KEY_CONFIG).spec(logging.getLogger("airbyte"))
    validator = Draft7Validator(spec.connectionSpecification)

    assert list(validator.iter_errors(_OAUTH_CONFIG)) == []
    assert list(validator.iter_errors(_API_KEY_CONFIG)) == []
    assert spec.connectionSpecification["properties"]["credentials"]["oneOf"][0]["title"] == "OAuth2.0"
    assert spec.advanced_auth.predicate_key == ["credentials", "auth_type"]
    assert spec.advanced_auth.predicate_value == "OAuth2.0"


def test_flat_api_key_config_is_migrated_into_credentials(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/ad_account", json=_ACCOUNT)

    source = _source(dict(_LEGACY_CONFIG))
    status = source.check(logging.getLogger("airbyte"), _LEGACY_CONFIG)

    assert status.status == Status.SUCCEEDED
    assert source._config["credentials"] == {"auth_type": "API Key", "api_key": "test-key"}
    [request] = _api_requests(requests_mock)
    assert request.headers["Authorization"] == "Bearer test-key"


def test_migration_leaves_oauth_config_unchanged() -> None:
    source = _source({**_OAUTH_CONFIG, "credentials": dict(_OAUTH_CONFIG["credentials"])})

    assert source._config["credentials"] == _OAUTH_CONFIG["credentials"]


@pytest.mark.parametrize("config", [_LEGACY_CONFIG, _API_KEY_CONFIG], ids=["legacy", "api_key"])
def test_api_key_sends_no_ad_account_header(requests_mock: Mocker, config: dict) -> None:
    requests_mock.get(f"{_URL}/ad_account", json=_ACCOUNT)

    output = read(_source(dict(config)), dict(config), CatalogBuilder().with_stream("ad_account", SyncMode.full_refresh).build())

    assert output.errors == []
    [request] = _api_requests(requests_mock)
    assert request.headers["Authorization"] == "Bearer test-key"
    assert "OpenAI-Ad-Account" not in request.headers


@freeze_time("2026-09-15T12:00:00Z")
def test_oauth_refreshes_the_token_and_selects_the_ad_account(requests_mock: Mocker) -> None:
    _mock_token(requests_mock)
    requests_mock.get(f"{_URL}/ad_account", json=_ACCOUNT)
    config = {**_OAUTH_CONFIG, "credentials": dict(_OAUTH_CONFIG["credentials"])}

    output = read(_source(config), config, CatalogBuilder().with_stream("ad_account", SyncMode.full_refresh).build())

    assert output.errors == []
    [token_request] = [request for request in requests_mock.request_history if request.url == _TOKEN_URL]
    assert parse_qs(token_request.text) == {
        "grant_type": ["refresh_token"],
        "client_id": ["client-id"],
        "client_secret": ["client-secret"],
        "refresh_token": ["refresh-1"],
    }
    [request] = _api_requests(requests_mock)
    assert request.headers["Authorization"] == "Bearer access-1"
    assert request.headers["OpenAI-Ad-Account"] == "adacct_123"


@freeze_time("2026-09-15T12:00:00Z")
def test_oauth_conversions_post_selects_the_ad_account(requests_mock: Mocker) -> None:
    _mock_token(requests_mock)
    requests_mock.get(f"{_URL}/campaigns?limit=500", complete_qs=True, json={"object": "list", "data": [{"id": "cmpn_1"}], "has_more": False})
    requests_mock.post(f"{_URL}/conversions/insights", json={"object": "list", "data": [], "count": 0})
    config = {**_OAUTH_CONFIG, "credentials": dict(_OAUTH_CONFIG["credentials"])}

    output = read(_source(config), config, CatalogBuilder().with_stream("campaign_conversions", SyncMode.full_refresh).build())

    assert output.errors == []
    [post] = [request for request in _api_requests(requests_mock) if request.method == "POST"]
    assert post.headers["OpenAI-Ad-Account"] == "adacct_123"
    assert post.headers["Content-Type"] == "application/json"


@freeze_time("2026-09-15T12:00:00Z")
def test_oauth_saves_a_rotated_refresh_token(requests_mock: Mocker, capsys: pytest.CaptureFixture[str]) -> None:
    _mock_token(requests_mock, refresh_token="refresh-2")
    requests_mock.get(f"{_URL}/ad_account", json=_ACCOUNT)
    config = {**_OAUTH_CONFIG, "credentials": dict(_OAUTH_CONFIG["credentials"])}

    output = read(_source(config), config, CatalogBuilder().with_stream("ad_account", SyncMode.full_refresh).build())

    # The CDK prints the updated config as a control message on stdout, outside the captured read output.
    controls = [json.loads(line)["control"] for line in capsys.readouterr().out.splitlines() if '"type":"CONTROL"' in line]
    assert output.errors == []
    assert controls[-1]["connectorConfig"]["config"]["credentials"]["refresh_token"] == "refresh-2"
