# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"
NESTED_FIELDS = {
    "realm_id": "realm-id",
    "auth_type": "oauth2.0",
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "refresh-token",
    "access_token": "access-token",
    "token_expiry_date": "2025-01-01T00:00:00Z",
}


def migrate_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
    migrated_config = source._migrate_and_transform_config(None, config)
    assert migrated_config is not None
    return migrated_config


def connector_config_control_message(output: str) -> Mapping[str, Any]:
    control_messages = []
    for line in output.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("type") == "CONTROL" and message.get("control", {}).get("type") == "CONNECTOR_CONFIG":
            control_messages.append(message)

    assert len(control_messages) == 1
    return control_messages[0]


def test_migrates_nested_credentials_to_root(capsys):
    config = {
        "credentials": NESTED_FIELDS,
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": True,
    }

    migrated_config = migrate_config(config)

    assert migrated_config == {
        **NESTED_FIELDS,
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": True,
    }
    control_message = connector_config_control_message(capsys.readouterr().out)
    assert control_message["control"]["connectorConfig"]["config"] == migrated_config


def test_migrates_numeric_realm_id_to_string():
    config = {
        "credentials": {**NESTED_FIELDS, "realm_id": 123},
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": False,
    }

    migrated_config = migrate_config(config)

    assert migrated_config["realm_id"] == "123"
    assert isinstance(migrated_config["realm_id"], str)


def test_does_not_add_missing_nested_fields_as_none():
    config = {
        "credentials": {key: value for key, value in NESTED_FIELDS.items() if key != "token_expiry_date"},
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": False,
    }

    migrated_config = migrate_config(config)

    assert migrated_config == {
        **config["credentials"],
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": False,
    }
    assert "token_expiry_date" not in migrated_config


def test_does_not_change_current_config():
    config = {
        **NESTED_FIELDS,
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": False,
    }
    original_config = deepcopy(config)

    migrated_config = migrate_config(config)

    assert migrated_config == original_config


def test_root_value_wins_over_stale_nested_value():
    config = {
        **NESTED_FIELDS,
        "client_id": "current-client-id",
        "credentials": {
            **NESTED_FIELDS,
            "client_id": "stale-client-id",
        },
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": True,
    }

    migrated_config = migrate_config(config)

    assert migrated_config["client_id"] == "current-client-id"
    assert migrated_config == {
        **NESTED_FIELDS,
        "client_id": "current-client-id",
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": True,
    }
