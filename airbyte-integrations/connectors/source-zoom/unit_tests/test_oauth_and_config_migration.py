# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests_mock
import yaml

from airbyte_cdk.models import FailureType, Status, SyncMode, Type
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
    assert manifest["spec"]["connection_specification"]["properties"]["credentials"]["oneOf"][0]["required"] == [
        "auth_type",
        "client_id",
        "client_secret",
        "refresh_token",
    ]


def test_flat_s2s_config_migrates_to_credentials():
    flat_config = {
        "account_id": "test_account_id",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_endpoint": TOKEN_URL,
    }

    assert _source(flat_config)._config == {
        "credentials": {
            "auth_type": "server_to_server",
            "account_id": "test_account_id",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "authorization_endpoint": TOKEN_URL,
        }
    }


def test_already_nested_s2s_and_oauth_configs_are_unchanged():
    for config in (S2S_CONFIG, OAUTH_CONFIG):
        assert _source(config)._config == config


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


def test_nested_s2s_config_requests_account_credentials_and_uses_bearer_token():
    expected_basic = base64.b64encode(b"test_client_id:test_client_secret").decode()
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(TOKEN_URL, json={"access_token": "s2s_access_token", "expires_in": 3599})
        users_mock = mocker.get(USERS_URL, json={"users": [{"id": "u1"}], "next_page_token": ""})

        output = _read(S2S_CONFIG)

    assert [record.record.data["id"] for record in output.records] == ["u1"]
    assert parse_qs(urlparse(token_mock.request_history[0].url).query, keep_blank_values=True) == {
        "grant_type": ["account_credentials"],
        "account_id": ["test_account_id"],
    }
    assert token_mock.request_history[0].headers["Authorization"] == f"Basic {expected_basic}"
    assert not token_mock.request_history[0].body
    assert users_mock.request_history[0].headers["Authorization"] == "Bearer s2s_access_token"


def test_oauth_refresh_rotates_refresh_token_and_uses_access_token():
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

    control_messages = output.get_message_by_types([Type.CONTROL])
    assert control_messages
    updated_credentials = control_messages[-1].control.connectorConfig.config["credentials"]
    assert updated_credentials["refresh_token"] == "new_rt"
    assert updated_credentials["access_token"] == "new_access_token"
    assert updated_credentials["token_expiry_date"]


def test_oauth_invalid_refresh_token_is_a_config_error_for_read_and_check():
    error_body = {"reason": "Invalid Token!", "error": "invalid_grant"}
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, status_code=400, json=error_body)
        users_mock = mocker.get(USERS_URL, json={"users": [], "next_page_token": ""})

        output = _read(OAUTH_CONFIG, expecting_exception=True)

    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert users_mock.call_count == 0

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, status_code=400, json=error_body)
        status = _check(OAUTH_CONFIG)

    assert status.status == Status.FAILED
    assert "invalid_grant" in status.message


def test_oauth_access_token_expiry_code_124_refreshes_and_retries_request():
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
