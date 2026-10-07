# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
from pathlib import Path

import pytest
from conftest import _MANIFEST_PATH, base_config, legacy_flat_config

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_TOKEN_REQUEST_BODY = "grant_type=refresh_token&refresh_token=test-refresh-token"
_ADS_URL = "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/ads"
_FALLBACK_USER_AGENT = "airbyte:source-reddit-ads:v1"
_EXPECTED_BASIC = "Basic " + base64.b64encode(b"test-client-id:test-client-secret").decode()


def _read_ads_with_config(config):
    catalog = CatalogBuilder().with_stream("ad", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body='{"access_token":"test-access-token","expires_in":3600}', status_code=200),
        )
        http_mocker.get(HttpRequest(_ADS_URL), HttpResponse(body='{"data":[]}', status_code=200))
        output = read(_get_source(config, catalog), config, catalog)
    return output, http_mocker


def _get_source(config, catalog=None, config_path=None):
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        config_path=config_path,
    )


def _token_request_headers(http_mocker):
    token_requests = [request for request in http_mocker._mocker.request_history if request.method == "POST" and request.url == _TOKEN_URL]
    assert len(token_requests) == 1
    return token_requests[0].headers


def _control_messages(capsys) -> list[dict]:
    messages = []
    for line in capsys.readouterr().out.splitlines():
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if isinstance(message, dict) and message.get("type") == "CONTROL":
            messages.append(message)
    return messages


def _construct_with_config_file(config: dict, tmp_path: Path, capsys):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    capsys.readouterr()  # drop any earlier output
    _get_source(dict(config), config_path=str(config_path))
    return config_path, _control_messages(capsys)


def test_spec_has_credentials_oneof_and_oauth_predicate() -> None:
    source = _get_source(base_config())
    spec = source.resolved_manifest["spec"]
    connection_specification = spec["connection_specification"]
    properties = connection_specification["properties"]

    assert set(connection_specification["required"]) == {"credentials", "ad_account_id"}
    for field in ("client_id", "client_secret", "refresh_token"):
        assert field not in properties
    assert "user_agent" in properties

    options = properties["credentials"]["oneOf"]
    assert len(options) == 2
    assert options[0]["title"] == "Authenticate with Reddit"
    assert options[0]["properties"]["auth_type"]["const"] == "OAuth2.0"
    assert options[0]["properties"]["auth_type"]["default"] == "OAuth2.0"
    assert options[1]["title"] == "Use your own Reddit app"
    assert options[1]["properties"]["auth_type"]["const"] == "OwnApp"
    for option in options:
        assert set(option["required"]) == {"auth_type", "client_id", "client_secret", "refresh_token"}
        for field in ("client_id", "client_secret", "refresh_token"):
            assert field in option["properties"]

    advanced_auth = spec["advanced_auth"]
    assert advanced_auth["predicate_key"] == ["credentials", "auth_type"]
    assert advanced_auth["predicate_value"] == "OAuth2.0"
    oauth_config = advanced_auth["oauth_config_specification"]
    authorization = oauth_config["oauth_connector_input_specification"]["access_token_headers"]["Authorization"]
    assert "| b64encode" in authorization
    assert "base64encode" not in authorization
    output_properties = oauth_config["complete_oauth_output_specification"]["properties"]
    assert output_properties["refresh_token"]["path_in_connector_config"] == ["credentials", "refresh_token"]
    server_output_properties = oauth_config["complete_oauth_server_output_specification"]["properties"]
    assert server_output_properties["client_id"]["path_in_connector_config"] == ["credentials", "client_id"]
    assert server_output_properties["client_secret"]["path_in_connector_config"] == ["credentials", "client_secret"]


def test_legacy_flat_config_migrates_and_emits_control_message(tmp_path, capsys) -> None:
    config = legacy_flat_config()
    config_path, controls = _construct_with_config_file(config, tmp_path, capsys)

    expected_credentials = {
        "auth_type": "OwnApp",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
    }
    assert len(controls) == 1
    control = controls[0]
    assert control["control"]["type"] == "CONNECTOR_CONFIG"
    emitted_config = control["control"]["connectorConfig"]["config"]
    assert emitted_config["credentials"] == expected_credentials
    # flat keys are left in place
    for field in ("client_id", "client_secret", "refresh_token"):
        assert emitted_config[field] == f"test-{field.replace('_', '-')}"
    rewritten = json.loads(config_path.read_text())
    assert rewritten["credentials"] == expected_credentials


@pytest.mark.parametrize("auth_type", ["OwnApp", "OAuth2.0"])
def test_nested_config_is_not_re_migrated(auth_type: str, tmp_path, capsys) -> None:
    config = base_config()
    config["credentials"]["auth_type"] = auth_type
    config_path, controls = _construct_with_config_file(config, tmp_path, capsys)

    assert controls == []
    assert json.loads(config_path.read_text())["credentials"]["auth_type"] == auth_type


def test_oauth_credentials_win_over_stale_flat_keys(tmp_path, capsys) -> None:
    config = base_config()
    config["credentials"]["auth_type"] = "OAuth2.0"
    config["client_id"] = "stale-flat-client-id"
    config["client_secret"] = "stale-flat-secret"
    config["refresh_token"] = "stale-flat-refresh"
    config_path, controls = _construct_with_config_file(config, tmp_path, capsys)

    assert controls == []
    assert json.loads(config_path.read_text())["credentials"]["client_id"] == "test-client-id"


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda c: c, id="flat"),
        pytest.param(lambda c: c.update({"credentials": {}}), id="flat+empty-credentials"),
        pytest.param(
            lambda c: c.update({"credentials": {"client_id": "x", "client_secret": "y", "refresh_token": "z"}}),
            id="flat+credentials-no-auth-type",
        ),
        pytest.param(lambda c: c.update({"client_id": "12345"}), id="numeric-client-id"),
    ],
)
def test_migration_never_produces_oauth_and_preserves_string_types(mutate, capsys) -> None:
    config = legacy_flat_config()
    mutate(config)
    capsys.readouterr()
    source = _get_source(config)

    migrated = source._config["credentials"]
    assert migrated["auth_type"] == "OwnApp"
    assert isinstance(migrated["client_id"], str)
    # The CDK migrates a shallow copy, so when `credentials` already exists the
    # in-place mutation leaves it equal to the input and no control message is
    # emitted; a purely flat config does emit one.
    expected_controls = 0 if config.get("credentials") is not None else 1
    assert len(_control_messages(capsys)) == expected_controls


def test_no_migration_value_contains_oauth_literal() -> None:
    source = _get_source(base_config())
    rules = source.resolved_manifest["spec"]["config_normalization_rules"]
    for migration in rules["config_migrations"]:
        for transformation in migration["transformations"]:
            for field in transformation["fields"]:
                assert "OAuth2.0" not in field.get("value", "")


def test_token_refresh_uses_nested_credentials_for_basic_auth() -> None:
    config = base_config()
    config["client_id"] = "stale-flat-client-id"
    config["client_secret"] = "stale-flat-secret"
    output, http_mocker = _read_ads_with_config(config)

    assert output.errors == []
    headers = _token_request_headers(http_mocker)
    assert headers["Authorization"] == _EXPECTED_BASIC


@pytest.mark.parametrize("missing_or_empty", ["missing", "empty"])
def test_token_refresh_falls_back_to_airbyte_user_agent(missing_or_empty: str) -> None:
    config = base_config()
    if missing_or_empty == "missing":
        del config["user_agent"]
    else:
        config["user_agent"] = ""

    output, http_mocker = _read_ads_with_config(config)

    assert output.errors == []
    headers = _token_request_headers(http_mocker)
    assert headers["User-Agent"] == _FALLBACK_USER_AGENT
    assert headers["Authorization"] == _EXPECTED_BASIC


def test_token_refresh_sends_configured_user_agent() -> None:
    output, http_mocker = _read_ads_with_config(base_config())

    assert output.errors == []
    headers = _token_request_headers(http_mocker)
    assert headers["User-Agent"] == "airbyte:reddit-ads-sync:v1.0 (by /u/airbyte)"
    assert headers["Authorization"] == _EXPECTED_BASIC


def test_full_read_with_legacy_flat_config_succeeds() -> None:
    output, http_mocker = _read_ads_with_config(legacy_flat_config())

    assert output.errors == []
    headers = _token_request_headers(http_mocker)
    assert headers["Authorization"] == _EXPECTED_BASIC
    token_requests = [request for request in http_mocker._mocker.request_history if request.method == "POST"]
    assert token_requests[0].text == _TOKEN_REQUEST_BODY
