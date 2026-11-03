# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Authentication tests for source-pipedrive.

OAuth is the first `credentials` option and `advanced_auth` describes the Declarative OAuth flow.
Flat configs (a top-level `api_token`) are wrapped into `credentials.auth_type == "api_token"` by
`config_normalization_rules` and keep working; the token travels in the `x-api-token` header.
API-token requests use the shared host (`https://api.pipedrive.com/v1/`, `/api/v2/`); OAuth
requests go to the company host from the token response (`credentials.api_domain`) under `/api/`.
"""

import base64
import copy
import logging

import pytest
import requests_mock
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
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


def _oauth_config(**credentials) -> dict:
    # A fresh copy per read: the CDK writes refreshed tokens into the config's credentials in place.
    config = copy.deepcopy(_CONFIG_OAUTH)
    config["credentials"].update(credentials)
    return config


_TOKEN_RESPONSE = {"access_token": "at", "refresh_token": "rt2", "expires_in": 3600, "api_domain": "https://acme.pipedrive.com"}
_CURRENCIES_RESPONSE = {"success": True, "data": [{"id": 1, "code": "USD"}]}
_DEALS_RESPONSE = {"data": [{"id": 1, "update_time": "2024-02-01T00:00:00Z"}], "additional_data": {"next_cursor": None}}


def _sync(stream_name: str, config: dict):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def test_spec_oauth_is_first_option_and_advanced_auth_present():
    spec = yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]

    credentials = spec["connection_specification"]["properties"]["credentials"]
    # Not required at the top level (the spec backward-compatibility check cannot see the migration); each option
    # requires its own fields.
    assert "required" not in spec["connection_specification"]
    assert credentials["oneOf"][1]["required"] == ["auth_type", "api_token"]
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
    assert oauth_input["access_token_headers"]["Authorization"] == "Basic {{ (client_id_value ~ ':' ~ client_secret_value) | b64encode }}"

    # Every value the platform writes must land on a property of the OAuth option.
    oauth_properties = credentials["oneOf"][0]["properties"]
    config_spec = advanced_auth["oauth_config_specification"]
    for section in ("complete_oauth_output_specification", "complete_oauth_server_output_specification"):
        for name, field in config_spec[section]["properties"].items():
            assert field["path_in_connector_config"] == ["credentials", name]
            assert name in oauth_properties
    assert set(config_spec["complete_oauth_output_specification"]["properties"]) == {
        "access_token",
        "refresh_token",
        "token_expiry_date",
        "api_domain",
    }
    assert set(config_spec["complete_oauth_server_output_specification"]["properties"]) == {"client_id", "client_secret"}

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
    # Only the migrations read the flat key (with `config.get`); requests read `credentials`.
    assert "config['api_token']" not in raw_text


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
        assert len(_sync("currencies", _oauth_config()).records) == 1
        assert len(_sync("deals", _oauth_config()).records) == 1

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
    config = _oauth_config(access_token="stored", token_expiry_date="2999-01-01T00:00:00.000Z")

    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth.pipedrive.com/oauth/token", json=_TOKEN_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", json=_CURRENCIES_RESPONSE)
        output = _sync("currencies", config)

    assert len(output.records) == 1
    assert [r.method for r in mocker.request_history] == ["GET"]
    assert mocker.request_history[0].headers["Authorization"] == "Bearer stored"


_OAUTH_401 = {"status_code": 401, "json": {"success": False, "error": "unauthorized access", "errorCode": 401}}


def test_oauth_401_on_a_stale_token_refreshes_once_and_retries() -> None:
    # A request signed just before the expiry instant can reach Pipedrive after it; one refresh fixes it.
    config = _oauth_config(access_token="stale", token_expiry_date="2999-01-01T00:00:00.000Z")
    sent = []

    def currencies(request, context):
        # The CDK re-signs the same request object on retry, so the header is recorded when it is sent.
        sent.append(request.headers["Authorization"])
        if len(sent) == 1:
            context.status_code = 401
            return _OAUTH_401["json"]
        return _CURRENCIES_RESPONSE

    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth.pipedrive.com/oauth/token", json=_TOKEN_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", json=currencies)
        output = _sync("currencies", config)

    assert len(output.records) == 1
    assert not output.errors
    assert [r.method for r in mocker.request_history] == ["GET", "POST", "GET"]
    assert sent == ["Bearer stale", "Bearer at"]


def test_oauth_401_after_a_refresh_fails_as_config_error() -> None:
    config = _oauth_config()
    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth.pipedrive.com/oauth/token", json=_TOKEN_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", **_OAUTH_401)
        catalog = CatalogBuilder().with_stream("currencies", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "Refreshed OAuth access token is rejected" in error.message
    # The initial refresh, one forced refresh after the first 401, and no further attempts.
    assert [r.method for r in mocker.request_history] == ["POST", "GET", "POST", "GET"]


@pytest.mark.parametrize("error_code", [None, 403])
def test_oauth_401_without_pipedrive_error_code_keeps_the_re_authenticate_message(error_code) -> None:
    # Only Pipedrive's JSON 401 triggers the refresh; any other 401 body reaches `unauthorized`.
    config = _oauth_config()
    body = {"success": False, "error": "unauthorized access"}
    if error_code is not None:
        body["errorCode"] = error_code
    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth.pipedrive.com/oauth/token", json=_TOKEN_RESPONSE)
        mocker.get("https://acme.pipedrive.com/api/v1/currencies", status_code=401, json=body)
        catalog = CatalogBuilder().with_stream("currencies", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "OAuth access token (401: unauthorized access)" in error.message
    assert "Re-authenticate the source" in error.message
    assert [r.method for r in mocker.request_history] == ["POST", "GET"]


def test_api_token_401_keeps_the_token_instructions() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.pipedrive.com/v1/currencies",
            status_code=401,
            json={"success": False, "error": "unauthorized access", "errorCode": 401},
        )
        catalog = CatalogBuilder().with_stream("currencies", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG_MIGRATED), _CONFIG_MIGRATED, catalog, expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "rejected the API token (401: unauthorized access)" in error.message
    assert "OAuth" not in error.message
    # A token 401 is never retried: there is nothing to refresh.
    assert len(mocker.request_history) == 1


@pytest.mark.parametrize(
    "api_domain",
    [
        "https://acme.pipedrive.com.example.io",
        "https://example.io/?x=https://acme.pipedrive.com",
        "http://acme.pipedrive.com",
        "https://acme.pipedrive.com/",
        "https://user@acme.pipedrive.com",
    ],
)
def test_oauth_rejects_an_api_domain_outside_pipedrive(api_domain) -> None:
    # The Bearer token goes to `api_domain`, so anything but https://<company>.pipedrive.com fails before any request.
    config = _oauth_config(api_domain=api_domain)
    with requests_mock.Mocker() as mocker:
        catalog = CatalogBuilder().with_stream("currencies", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)

    assert mocker.request_history == []
    assert output.errors[0].trace.error.failure_type == FailureType.config_error


def test_legacy_top_level_token_stays_a_hidden_secret() -> None:
    # Migrated configs keep the top-level token; the spec must keep it masked.
    api_token = yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]["connection_specification"]["properties"]["api_token"]
    assert api_token["airbyte_secret"] is True
    assert api_token["airbyte_hidden"] is True


def test_each_stream_uses_the_requester_for_its_api_version() -> None:
    # Both bases resolve to the same host with a token, so only OAuth (the default) would catch a wrong ref:
    # <api_domain>/api/api/v2/... or <api_domain>/v1/....
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    v2_url_base = manifest["definitions"]["v2_requester"]["url_base"]
    v1_url_base = manifest["definitions"]["base_requester"]["url_base"]
    assert v1_url_base != v2_url_base

    def requesters(node):
        if isinstance(node, dict):
            if node.get("type") == "HttpRequester":
                yield node
            for value in node.values():
                yield from requesters(value)
        elif isinstance(node, list):
            for item in node:
                yield from requesters(item)

    checked = 0
    for requester in requesters(manifest["streams"]):
        path = requester["path"]
        assert path.startswith(("v1/", "api/v2/")), path
        assert requester["url_base"] == (v2_url_base if path.startswith("api/v2/") else v1_url_base), path
        checked += 1
    assert checked >= 37
