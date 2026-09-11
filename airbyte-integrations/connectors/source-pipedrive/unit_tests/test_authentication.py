# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-pipedrive` authentication.

OAuth is the default authentication method for source-pipedrive: it is the first
`oneOf` option of the `credentials` spec property and `advanced_auth` describes
the OAuth flow. Legacy flat configs (a top-level `api_token`) are migrated into
`credentials.auth_type == "api_token"` by `config_normalization_rules` and keep
working, with the token sent as the `x-api-token` request header.
"""

import base64
import json
import logging
from pathlib import Path

import requests_mock
import yaml
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

_CONFIG_MIGRATED = {
    "credentials": {"auth_type": "api_token", "api_token": "tok"},
    "replication_start_date": "2024-01-01 00:00:00Z",
}

_CONFIG_FLAT = {
    "api_token": "tok",
    "replication_start_date": "2024-01-01 00:00:00Z",
}

_CONFIG_OAUTH = {
    "credentials": {
        "auth_type": "oauth2.0",
        "client_id": "cid",
        "client_secret": "cs",
        "refresh_token": "rt",
        "api_domain": "https://acme.pipedrive.com",
    },
    "replication_start_date": "2024-01-01 00:00:00Z",
}

_CURRENCIES_RESPONSE = {"success": True, "data": [{"id": 1, "code": "USD"}]}


def _sync(stream_name: str, config: dict):
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog)


def _emitted_migrated_configs(capsys) -> list:
    """Return connector-config control messages printed to stdout during a sync."""
    configs = []
    for line in capsys.readouterr().out.splitlines():
        try:
            message = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(message, dict) and message.get("type") == "CONTROL" and message.get("control", {}).get("type") == "CONNECTOR_CONFIG":
            configs.append(message["control"]["connectorConfig"]["config"])
    return configs


def test_spec_oauth_is_first_option_and_advanced_auth_present():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    spec = manifest["spec"]

    credentials = spec["connection_specification"]["properties"]["credentials"]
    assert credentials["oneOf"][0]["properties"]["auth_type"]["const"] == "oauth2.0"
    assert credentials["oneOf"][1]["properties"]["auth_type"]["const"] == "api_token"

    advanced_auth = spec["advanced_auth"]
    assert advanced_auth["predicate_key"] == ["credentials", "auth_type"]
    assert advanced_auth["predicate_value"] == "oauth2.0"

    oauth_input = advanced_auth["oauth_config_specification"]["oauth_connector_input_specification"]
    assert "oauth.pipedrive.com/oauth/authorize" in oauth_input["consent_url"]
    assert oauth_input["access_token_url"] == "https://oauth.pipedrive.com/oauth/token"

    source = get_source(config=_CONFIG_MIGRATED)
    connector_spec = source.spec(logging.getLogger("airbyte"))
    assert connector_spec.advanced_auth is not None


def test_no_api_token_request_parameter_remains():
    raw_text = _MANIFEST_PATH.read_text()
    manifest = yaml.safe_load(raw_text)

    def _request_parameters(node):
        if isinstance(node, dict):
            if "request_parameters" in node:
                yield node["request_parameters"]
            for value in node.values():
                yield from _request_parameters(value)
        elif isinstance(node, list):
            for item in node:
                yield from _request_parameters(item)

    requester_nodes = list(manifest["definitions"]["streams"].values()) + [manifest["definitions"]["base_requester"]]
    for node in requester_nodes:
        for request_parameters in _request_parameters(node):
            assert "api_token" not in request_parameters

    assert "request_parameters" not in manifest["definitions"]["base_requester"]
    # The only remaining reference is the config migration, which reads the
    # legacy flat `api_token` key to wrap it into `credentials`.
    assert raw_text.count("config['api_token']") == 1


def test_flat_config_is_migrated_and_sends_header(capsys):
    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.pipedrive.com/v1/currencies", json=_CURRENCIES_RESPONSE)
        output = _sync("currencies", dict(_CONFIG_FLAT))

    assert len(output.records) == 1
    assert output.records[0].record.data["code"] == "USD"

    request = mocker.request_history[0]
    assert request.url.startswith("https://api.pipedrive.com/v1/currencies")
    assert request.headers["x-api-token"] == "tok"
    assert "api_token" not in request.qs

    migrated_configs = _emitted_migrated_configs(capsys)
    assert migrated_configs, "expected a CONNECTOR_CONFIG control message with the migrated config"
    assert migrated_configs[-1]["credentials"] == {"auth_type": "api_token", "api_token": "tok"}


def test_migrated_config_sends_same_request():
    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.pipedrive.com/v1/currencies", json=_CURRENCIES_RESPONSE)
        output = _sync("currencies", dict(_CONFIG_MIGRATED))

    assert len(output.records) == 1

    request = mocker.request_history[0]
    assert request.url.startswith("https://api.pipedrive.com/v1/currencies")
    assert request.headers["x-api-token"] == "tok"
    assert "api_token" not in request.qs


def test_oauth_config_uses_api_domain_and_bearer():
    expected_basic = base64.b64encode(b"cid:cs").decode()

    with requests_mock.Mocker() as mocker:
        mocker.post(
            "https://oauth.pipedrive.com/oauth/token",
            json={
                "access_token": "at",
                "refresh_token": "rt2",
                "expires_in": 3600,
                "api_domain": "https://acme.pipedrive.com",
            },
        )
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", json=_CURRENCIES_RESPONSE)
        output = _sync("currencies", dict(_CONFIG_OAUTH))

    assert len(output.records) == 1

    get_requests = [r for r in mocker.request_history if r.method == "GET"]
    assert get_requests[0].url.startswith("https://acme.pipedrive.com/api/v1/currencies")
    assert get_requests[0].headers["Authorization"] == "Bearer at"

    token_requests = [r for r in mocker.request_history if r.method == "POST"]
    assert token_requests[0].headers["Authorization"] == f"Basic {expected_basic}"
