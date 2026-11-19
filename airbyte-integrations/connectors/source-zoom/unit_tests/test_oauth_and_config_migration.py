# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
INVALID_CONFIG_PATH = Path(__file__).parents[1] / "integration_tests" / "invalid_config.json"
TOKEN_URL = "https://zoom.us/oauth/token"
USERS_URL = "https://api.zoom.us/v2/users"
S2S_CONFIG = {
    "credentials": {
        "auth_type": "server_to_server",
        "account_id": "test_account_id",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_endpoint": TOKEN_URL,
    }
}
OAUTH_CONFIG = {
    "credentials": {
        "auth_type": "oauth2.0",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "old_rt",
    }
}
S2S_CONFIG_WITHOUT_ENDPOINT = {"credentials": {k: v for k, v in S2S_CONFIG["credentials"].items() if k != "authorization_endpoint"}}
ZOOMGOV_TOKEN_URL = "https://zoomgov.com/oauth/token"


def _source(config):
    return YamlDeclarativeSource(
        path_to_yaml=str(MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=deepcopy(config),
        state=StateBuilder().build(),
    )


def _read(config, stream_name="users", expecting_exception=False):
    source = _source(config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog, expecting_exception=expecting_exception)


def _check(config):
    source = _source(config)
    return source.check(logger=source.logger, config=config)


def _emitted_configs(capsys):
    """CONNECTOR_CONFIG control messages, which CDK >= 7.37 prints only to stdout (airbyte-python-cdk#1145)."""
    lines = capsys.readouterr().out.splitlines()
    return [json.loads(line)["control"]["connectorConfig"]["config"] for line in lines if '"type":"CONTROL"' in line]


def test_spec_exposes_oauth_as_the_first_authentication_option():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    source = _source({})
    spec = source.spec(logger=source.logger)
    credentials = spec.connectionSpecification["properties"]["credentials"]
    advanced_auth = spec.advanced_auth
    oauth_input = advanced_auth.oauth_config_specification.oauth_connector_input_specification

    assert [option["title"] for option in credentials["oneOf"]] == ["OAuth2.0", "Server-to-Server OAuth"]
    assert spec.connectionSpecification["required"] == ["credentials"]
    assert advanced_auth.predicate_key == ["credentials", "auth_type"]
    assert advanced_auth.predicate_value == "oauth2.0"
    assert urlparse(oauth_input.consent_url).netloc == "zoom.us"
    assert urlparse(oauth_input.consent_url).path == "/oauth/authorize"
    oauth_option, s2s_option = manifest["spec"]["connection_specification"]["properties"]["credentials"]["oneOf"]
    assert oauth_option["required"] == ["auth_type", "client_id", "client_secret", "refresh_token"]
    assert s2s_option["required"] == ["auth_type", "account_id", "client_id", "client_secret"]
    assert {name for name, field in oauth_option["properties"].items() if field.get("airbyte_secret")} == {
        "client_secret",
        "refresh_token",
        "access_token",
    }
    assert {name for name, field in s2s_option["properties"].items() if field.get("airbyte_secret")} == {"client_secret"}

    # Only the platform's OAuth flow reads these, so nothing else fails if they break.
    oauth_input_spec = manifest["spec"]["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]
    assert parse_qs(urlparse(oauth_input_spec["consent_url"]).query) == {
        "response_type": ["code"],
        "client_id": ["{{client_id_value}}"],
        "redirect_uri": ["{{redirect_uri_value}}"],
        "state": ["{{state_value}}"],
    }
    assert oauth_input_spec["access_token_url"] == TOKEN_URL
    assert oauth_input_spec["access_token_params"] == {
        "grant_type": "authorization_code",
        "code": "{{ auth_code_value }}",
        "redirect_uri": "{{ redirect_uri_value }}",
    }
    assert oauth_input_spec["access_token_headers"] == {
        "Authorization": "Basic {{ (client_id_value ~ ':' ~ client_secret_value) | b64encode }}",
        "Content-Type": "application/x-www-form-urlencoded",
    }


def test_oauth_flow_writes_tokens_where_the_authenticator_reads_them():
    # Without `expires_in` the platform writes no token_expiry_date, so the create-time check refreshes and rotates the token.
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    updater = manifest["definitions"]["authenticator"]["authenticators"]["oauth2.0"]["refresh_token_updater"]
    oauth_spec = manifest["spec"]["advanced_auth"]["oauth_config_specification"]
    outputs = oauth_spec["complete_oauth_output_specification"]["properties"]
    server_outputs = oauth_spec["complete_oauth_server_output_specification"]["properties"]
    oauth_properties = manifest["spec"]["connection_specification"]["properties"]["credentials"]["oneOf"][0]["properties"]
    paths = [field["path_in_connector_config"] for field in [*outputs.values(), *server_outputs.values()]]

    assert {name: outputs[name]["path_in_connector_config"] for name in outputs} == {
        name: updater[f"{name}_config_path"] for name in ("access_token", "refresh_token", "token_expiry_date")
    }
    assert all(len(path) == 2 and path[0] == "credentials" and path[1] in oauth_properties for path in paths)
    assert {"access_token", "refresh_token", "expires_in"} <= set(oauth_spec["oauth_connector_input_specification"]["extract_output"])


@pytest.mark.parametrize("value", ["test_value", "1234567890"], ids=["alphanumeric", "digits_only"])
def test_flat_s2s_config_migrates_to_credentials(value):
    flat_config = {
        "account_id": value,
        "client_id": value,
        "client_secret": value,
        "authorization_endpoint": TOKEN_URL,
    }

    # Migrated values stay strings: interpolation would otherwise turn "1234567890" into an int that fails the spec.
    assert _source(flat_config)._config == {
        "credentials": {
            "auth_type": "server_to_server",
            "account_id": value,
            "client_id": value,
            "client_secret": value,
            "authorization_endpoint": TOKEN_URL,
        }
    }


def test_already_nested_s2s_and_oauth_configs_are_unchanged():
    for config in (S2S_CONFIG, OAUTH_CONFIG):
        assert _source(config)._config == config


def test_nested_oauth_config_drops_stale_flat_keys_and_keeps_its_credentials():
    # A PATCH of `credentials` onto a not yet migrated flat config merges both shapes. The flat client_secret must go:
    # the new spec no longer marks it as a secret, so a persisted copy would be stored in plain text.
    config = {**OAUTH_CONFIG, "account_id": "flat", "client_id": "flat", "client_secret": "flat", "authorization_endpoint": TOKEN_URL}

    assert _source(config)._config == OAUTH_CONFIG


def test_invalid_flat_config_migrates_without_account_id_and_check_fails():
    invalid_config = json.loads(INVALID_CONFIG_PATH.read_text())
    source = _source(invalid_config)

    assert source._config == {
        "credentials": {
            "auth_type": "server_to_server",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "authorization_endpoint": TOKEN_URL,
        }
    }

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, status_code=400, json={"reason": "Bad Request", "error": "invalid_request"})
        status = source.check(logger=source.logger, config=invalid_config)

    assert status.status == Status.FAILED


@pytest.mark.parametrize(
    "config, token_url",
    [
        (S2S_CONFIG, TOKEN_URL),
        (S2S_CONFIG_WITHOUT_ENDPOINT, TOKEN_URL),
        ({"credentials": {**S2S_CONFIG["credentials"], "authorization_endpoint": ZOOMGOV_TOKEN_URL}}, ZOOMGOV_TOKEN_URL),
    ],
    ids=["authorization_endpoint", "default_token_url", "custom_token_url"],
)
def test_nested_s2s_config_requests_account_credentials_and_uses_bearer_token(config, token_url):
    expected_basic = base64.b64encode(b"test_client_id:test_client_secret").decode()
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(token_url, json={"access_token": "s2s_access_token", "expires_in": 3599})
        users_mock = mocker.get(USERS_URL, json={"users": [{"id": "u1"}], "next_page_token": ""})

        output = _read(config)

    assert [record.record.data["id"] for record in output.records] == ["u1"]
    assert parse_qs(urlparse(token_mock.request_history[0].url).query, keep_blank_values=True) == {
        "grant_type": ["account_credentials"],
        "account_id": ["test_account_id"],
    }
    assert token_mock.request_history[0].headers["Authorization"] == f"Basic {expected_basic}"
    assert not token_mock.request_history[0].body
    assert users_mock.request_history[0].headers["Authorization"] == "Bearer s2s_access_token"


def test_oauth_refresh_rotates_refresh_token_and_uses_access_token(capsys):
    expected_basic = base64.b64encode(b"test_client_id:test_client_secret").decode()
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(
            TOKEN_URL,
            json={"access_token": "new_access_token", "refresh_token": "new_rt", "expires_in": 3599},
        )
        users_mock = mocker.get(USERS_URL, json={"users": [{"id": "u1"}], "next_page_token": ""})

        output = _read(OAUTH_CONFIG)

    assert [record.record.data["id"] for record in output.records] == ["u1"]
    assert token_mock.call_count == 1
    token_request = token_mock.request_history[0]
    assert parse_qs(urlparse(token_request.url).query, keep_blank_values=True) == {
        "grant_type": ["refresh_token"],
        "refresh_token": ["old_rt"],
    }
    assert token_request.headers["Authorization"] == f"Basic {expected_basic}"
    assert not token_request.body
    assert users_mock.request_history[0].headers["Authorization"] == "Bearer new_access_token"

    emitted_configs = _emitted_configs(capsys)
    assert len(emitted_configs) == 1
    updated_credentials = emitted_configs[0]["credentials"]
    assert updated_credentials["refresh_token"] == "new_rt"
    assert updated_credentials["access_token"] == "new_access_token"
    assert updated_credentials["token_expiry_date"]


@pytest.mark.parametrize(
    "status_code, error_body",
    [
        (400, {"reason": "Invalid Token!", "error": "invalid_grant"}),
        (401, {"reason": "Invalid Token!", "error": "invalid_request"}),
        (400, {"reason": "Invalid client_id or client_secret", "error": "invalid_client"}),
        (400, {"reason": "grant type refresh_token is not supported from token endpoint", "error": "unsupported_grant_type"}),
        (404, {"reason": "The application is disabled", "error": "invalid_client"}),
    ],
    ids=["invalid_grant", "invalid_request_401", "invalid_client", "unsupported_grant_type", "disabled_app"],
)
def test_oauth_rejected_refresh_is_a_config_error_for_read_and_check(status_code, error_body):
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, status_code=status_code, json=error_body)
        users_mock = mocker.get(USERS_URL, json={"users": [], "next_page_token": ""})

        output = _read(OAUTH_CONFIG, expecting_exception=True)

    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert users_mock.call_count == 0

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, status_code=status_code, json=error_body)
        status = _check(OAUTH_CONFIG)

    assert status.status == Status.FAILED
    assert error_body["error"] in status.message


def test_oauth_access_token_expiry_code_124_refreshes_and_retries_request(capsys):
    config = deepcopy(OAUTH_CONFIG)
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(
            TOKEN_URL,
            [
                {"json": {"access_token": "access_1", "refresh_token": "rotated_rt_1", "expires_in": 3599}},
                {"json": {"access_token": "access_2", "refresh_token": "rotated_rt_2", "expires_in": 3599}},
            ],
        )
        users_mock = mocker.get(
            USERS_URL,
            [
                {"json": {"users": [{"id": "u1"}], "next_page_token": "p2"}},
                {"status_code": 401, "json": {"code": 124, "message": "Invalid access token."}},
                {"json": {"users": [{"id": "u2"}], "next_page_token": ""}},
            ],
        )

        output = _read(config)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["u1", "u2"]
    assert token_mock.call_count == 2
    assert parse_qs(urlparse(token_mock.request_history[0].url).query)["refresh_token"] == ["old_rt"]
    assert parse_qs(urlparse(token_mock.request_history[1].url).query)["refresh_token"] == ["rotated_rt_1"]
    assert users_mock.call_count == 3
    assert [emitted["credentials"]["refresh_token"] for emitted in _emitted_configs(capsys)] == ["rotated_rt_1", "rotated_rt_2"]


def test_oauth_parent_and_child_requesters_share_one_token_refresh(capsys):
    # `meetings` has three requesters (users >> users/{id}/meetings >> meetings/{id}), each with its own authenticator.
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(
            TOKEN_URL,
            [{"json": {"access_token": f"access_{i}", "refresh_token": f"rotated_rt_{i}", "expires_in": 3599}} for i in (1, 2, 3)],
        )
        mocker.get(USERS_URL, json={"users": [{"id": "u1"}], "next_page_token": ""})
        mocker.get(f"{USERS_URL}/u1/meetings", json={"meetings": [{"id": 1}], "next_page_token": ""})
        mocker.get("https://api.zoom.us/v2/meetings/1", json={"id": 1, "topic": "t"})

        output = _read(OAUTH_CONFIG, "meetings")

    api_requests = [request for request in mocker.request_history if request.url.startswith("https://api.zoom.us/")]
    assert [record.record.data["id"] for record in output.records] == [1]
    assert token_mock.call_count == 1
    assert len(api_requests) == 3
    assert {request.headers["Authorization"] for request in api_requests} == {"Bearer access_1"}
    assert [emitted["credentials"]["refresh_token"] for emitted in _emitted_configs(capsys)] == ["rotated_rt_1"]
