# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the config migration that flattens the pre-4.0.0 nested `credentials` object.

`4.0.0` moved the OAuth fields to the root of the config without shipping a migration, so configs
created before it fail spec validation on the missing root fields. These tests pin both shapes:
a legacy nested config is flattened, and an already-flat config is left untouched.
"""

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

OAUTH_FIELDS = (
    "client_id",
    "client_secret",
    "refresh_token",
    "access_token",
    "token_expiry_date",
    "realm_id",
)

FLAT_CREDENTIALS = {
    "auth_type": "oauth2.0",
    "client_id": "a-client-id",
    "client_secret": "a-client-secret",
    "refresh_token": "a-refresh-token",
    "access_token": "an-access-token",
    "token_expiry_date": "2026-01-01T00:00:00+00:00",
    "realm_id": "1234567890",
}


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def migrate(manifest, config):
    return ConcurrentDeclarativeSource(source_config=manifest, config=config, catalog=None, state=None)._config


def flat_config():
    return {**FLAT_CREDENTIALS, "start_date": "2021-03-20T00:00:00Z", "sandbox": False}


def nested_config():
    return {
        "credentials": dict(FLAT_CREDENTIALS),
        "start_date": "2021-03-20T00:00:00Z",
        "sandbox": False,
    }


def test_nested_config_is_flattened(manifest):
    migrated = migrate(manifest, nested_config())

    assert migrated == flat_config()
    assert "credentials" not in migrated


def test_flat_config_is_unchanged(manifest):
    config = flat_config()

    assert migrate(manifest, config) == config


def test_realm_id_stays_a_string(manifest):
    """A numeric realm id must not be coerced to an int by the interpolation."""
    config = nested_config()
    config["credentials"]["realm_id"] = "1234567890"

    assert migrate(manifest, config)["realm_id"] == "1234567890"


@pytest.mark.parametrize("config_factory", [flat_config, nested_config], ids=["flat", "nested"])
def test_migrated_config_satisfies_the_spec(manifest, config_factory):
    migrated = migrate(manifest, config_factory())

    jsonschema.validate(migrated, manifest["spec"]["connection_specification"])


def test_migrated_config_is_persisted(manifest, tmp_path, capsys):
    """The flattened config must be written back and announced, or it reverts on the next sync."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(nested_config()))

    ConcurrentDeclarativeSource(
        source_config=manifest,
        config=nested_config(),
        catalog=None,
        state=None,
        config_path=str(config_path),
    )

    assert json.loads(config_path.read_text()) == flat_config()

    control_messages = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{") and json.loads(line).get("type") == "CONTROL"
    ]
    assert [message["control"]["connectorConfig"]["config"] for message in control_messages] == [flat_config()]


@pytest.mark.parametrize("field", OAUTH_FIELDS)
def test_root_value_wins_over_nested_value(manifest, field):
    """A config carrying both shapes keeps the root value, which is the one `4.0.0` writes to."""
    config = nested_config()
    config[field] = "root-value"
    config["credentials"][field] = "nested-value"

    assert migrate(manifest, config)[field] == "root-value"
