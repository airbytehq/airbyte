# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Authentication tests for source-pipedrive.

OAuth is the first `credentials` option and `advanced_auth` describes the Declarative OAuth flow.
Flat configs (a top-level `api_token`) are wrapped into `credentials.auth_type == "api_token"` by
`config_normalization_rules` and keep working; the token travels in the `x-api-token` header.
API-token requests use the shared host (`https://api.pipedrive.com/v1/`, `/api/v2/`); OAuth
requests go to the company host from the token response (`credentials.api_domain`) under `/api/`.
"""

import base64
import logging

import requests_mock
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG_MIGRATED = {
    "credentials": {"auth_type": "api_token", "api_token": "tok"},
    "replication_start_date": "2024-01-01T00:00:00Z",
}

_CONFIG_OAUTH = {
    "credentials": {
        "auth_type": "oauth2.0",
        "client_id": "cid",
        "client_secret": "cs",
        "refresh_token": "rt",
        "api_domain": "https://acme.pipedrive.com",
    },
    "replication_start_date": "2024-01-01T00:00:00Z",
}

_TOKEN_RESPONSE = {"access_token": "at", "refresh_token": "rt2", "expires_in": 3600, "api_domain": "https://acme.pipedrive.com"}
_CURRENCIES_RESPONSE = {"success": True, "data": [{"id": 1, "code": "USD"}]}
_DEALS_RESPONSE = {"data": [{"id": 1, "update_time": "2024-02-01T00:00:00Z"}], "additional_data": {"next_cursor": None}}


def _sync(stream_name: str, config: dict):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def test_spec_oauth_is_first_option_and_advanced_auth_present():
    spec = yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]

    credentials = spec["connection_specification"]["properties"]["credentials"]
    assert spec["connection_specification"]["required"] == ["credentials"]
    assert credentials["oneOf"][0]["properties"]["auth_type"]["const"] == "oauth2.0"
    assert "api_domain" in credentials["oneOf"][0]["required"]
    assert credentials["oneOf"][1]["properties"]["auth_type"]["const"] == "api_token"

    advanced_auth = spec["advanced_auth"]
    assert advanced_auth["predicate_key"] == ["credentials", "auth_type"]
    assert advanced_auth["predicate_value"] == "oauth2.0"
    oauth_input = advanced_auth["oauth_config_specification"]["oauth_connector_input_specification"]
    assert oauth_input["consent_url"].startswith("https://oauth.pipedrive.com/oauth/authorize?")
    assert oauth_input["access_token_url"] == "https://oauth.pipedrive.com/oauth/token"
    assert "api_domain" in oauth_input["extract_output"]

    assert get_source(_CONFIG_MIGRATED).spec(logging.getLogger("airbyte")).advanced_auth is not None


def test_no_api_token_request_parameter_remains():
    raw_text = _YAML_FILE_PATH.read_text()
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

    for stream in manifest["definitions"]["streams"].values():
        for request_parameters in _request_parameters(stream):
            assert "api_token" not in request_parameters
    # The only remaining reference reads the flat legacy key to wrap it into `credentials`.
    assert raw_text.count("config['api_token']") == 1


def test_migrated_config_sends_header_to_both_api_versions():
    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.pipedrive.com/v1/currencies", json=_CURRENCIES_RESPONSE)
        mocker.get("https://api.pipedrive.com/api/v2/deals", json=_DEALS_RESPONSE)
        assert len(_sync("currencies", dict(_CONFIG_MIGRATED)).records) == 1
        assert len(_sync("deals", dict(_CONFIG_MIGRATED)).records) == 1

    assert [r.url.split("?")[0] for r in mocker.request_history] == [
        "https://api.pipedrive.com/v1/currencies",
        "https://api.pipedrive.com/api/v2/deals",
    ]
    assert all(r.headers["x-api-token"] == "tok" and "api_token" not in r.qs for r in mocker.request_history)


def test_oauth_config_uses_company_host_for_both_api_versions():
    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth.pipedrive.com/oauth/token", json=_TOKEN_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", json=_CURRENCIES_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v2/deals", json=_DEALS_RESPONSE)
        assert len(_sync("currencies", dict(_CONFIG_OAUTH)).records) == 1
        assert len(_sync("deals", dict(_CONFIG_OAUTH)).records) == 1

    gets = [r for r in mocker.request_history if r.method == "GET"]
    assert [r.url.split("?")[0] for r in gets] == [
        "https://acme.pipedrive.com/api/v1/currencies",
        "https://acme.pipedrive.com/api/v2/deals",
    ]
    assert all(r.headers["Authorization"] == "Bearer at" for r in gets)

    refreshes = [r for r in mocker.request_history if r.method == "POST"]
    assert refreshes and refreshes[0].headers["Authorization"] == f"Basic {base64.b64encode(b'cid:cs').decode()}"
    assert refreshes[0].headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert "grant_type=refresh_token" in refreshes[0].text and "refresh_token=rt" in refreshes[0].text


def test_oauth_reuses_a_stored_access_token_until_the_platform_expiry_instant():
    config = dict(_CONFIG_OAUTH)
    config["credentials"] = {**_CONFIG_OAUTH["credentials"], "access_token": "stored", "token_expiry_date": "2999-01-01T00:00:00.000Z"}

    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth.pipedrive.com/oauth/token", json=_TOKEN_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", json=_CURRENCIES_RESPONSE)
        output = _sync("currencies", config)

    assert len(output.records) == 1
    assert [r.method for r in mocker.request_history] == ["GET"]
    assert mocker.request_history[0].headers["Authorization"] == "Bearer stored"
