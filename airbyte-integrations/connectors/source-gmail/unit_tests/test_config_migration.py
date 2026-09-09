#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json

import pytest

from .conftest import build_source


def _migrate(config, capsys):
    source = build_source(config)
    control_messages = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{") and json.loads(line).get("type") == "CONTROL"
    ]
    return source._config, control_messages


def test_complete_legacy_config_migrates_to_nested_credentials(capsys):
    config = {
        "client_id": "id",
        "client_secret": "secret",
        "client_refresh_token": "token",
        "include_spam_and_trash": False,
    }
    expected_credentials = {
        "auth_type": "Client",
        "client_id": "id",
        "client_secret": "secret",
        "client_refresh_token": "token",
    }

    migrated, control_messages = _migrate(config, capsys)

    assert migrated["credentials"] == expected_credentials
    assert len(control_messages) == 1
    assert control_messages[0]["control"]["type"] == "CONNECTOR_CONFIG"
    assert control_messages[0]["control"]["connectorConfig"]["config"]["credentials"] == expected_credentials


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            {"client_id": "", "client_secret": "", "client_refresh_token": ""},
            id="all_empty",
        ),
        pytest.param(
            {"client_secret": "secret", "client_refresh_token": "token"},
            id="client_id_missing",
        ),
        pytest.param(
            {"client_id": None, "client_secret": "secret", "client_refresh_token": "token"},
            id="client_id_null",
        ),
        pytest.param(
            {"client_id": "", "client_secret": "secret", "client_refresh_token": "token"},
            id="client_id_empty",
        ),
        pytest.param(
            {"client_id": "id", "client_refresh_token": "token"},
            id="client_secret_missing",
        ),
        pytest.param(
            {"client_id": "id", "client_secret": None, "client_refresh_token": "token"},
            id="client_secret_null",
        ),
        pytest.param(
            {"client_id": "id", "client_secret": "", "client_refresh_token": "token"},
            id="client_secret_empty",
        ),
        pytest.param(
            {"client_id": "id", "client_secret": "secret"},
            id="client_refresh_token_missing",
        ),
        pytest.param(
            {"client_id": "id", "client_secret": "secret", "client_refresh_token": None},
            id="client_refresh_token_null",
        ),
        pytest.param(
            {"client_id": "id", "client_secret": "secret", "client_refresh_token": ""},
            id="client_refresh_token_empty",
        ),
    ],
)
def test_incomplete_legacy_config_is_not_migrated(config, capsys):
    migrated, control_messages = _migrate(config, capsys)

    assert "credentials" not in migrated
    assert control_messages == []


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            {
                "credentials": {
                    "auth_type": "Client",
                    "client_id": "id",
                    "client_secret": "secret",
                    "client_refresh_token": "token",
                }
            },
            id="nested_oauth",
        ),
        pytest.param(
            {"credentials": {"auth_type": "Service", "service_account_info": "{}"}},
            id="nested_service",
        ),
        pytest.param(
            {
                "client_id": "old",
                "client_secret": "old",
                "client_refresh_token": "old",
                "credentials": {
                    "auth_type": "Client",
                    "client_id": "id",
                    "client_secret": "secret",
                    "client_refresh_token": "token",
                },
            },
            id="nested_oauth_with_stale_legacy_fields",
        ),
    ],
)
def test_already_nested_config_is_unchanged(config, capsys):
    migrated, control_messages = _migrate(config, capsys)

    assert migrated == config
    assert control_messages == []


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            {
                "client_id": "id",
                "client_secret": "secret",
                "client_refresh_token": "token",
                "include_spam_and_trash": False,
            },
            id="complete_legacy_config",
        ),
        pytest.param(
            {"client_id": "", "client_secret": "", "client_refresh_token": ""},
            id="all_empty",
        ),
    ],
)
def test_migration_never_writes_empty_secret_fields(manifest, config, capsys):
    oauth_properties = manifest["spec"]["connection_specification"]["properties"]["credentials"]["oneOf"][0]["properties"]
    secret_names = {name for name, prop in oauth_properties.items() if prop.get("airbyte_secret") is True}

    _, control_messages = _migrate(config, capsys)

    for message in control_messages:
        credentials = message["control"]["connectorConfig"]["config"].get("credentials", {})
        assert all(credentials.get(name) not in {"", None} for name in secret_names)
