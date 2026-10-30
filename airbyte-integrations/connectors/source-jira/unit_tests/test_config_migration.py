# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from copy import deepcopy
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


_CONNECTOR_DIR = Path(__file__).parent.parent
_YAML_FILE_PATH = _CONNECTOR_DIR / "manifest.yaml"
sys.path.insert(0, str(_CONNECTOR_DIR))


def _migrate(config: dict) -> dict:
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        config=deepcopy(config),
    )
    return source._config


def test_oauth_config_gains_no_empty_legacy_fields() -> None:
    config = {
        "credentials": {
            "auth_type": "OAuth 2.0",
            "client_id": "id",
            "client_secret": "secret",
            "refresh_token": "rt",
        },
        "domain": "x.atlassian.net",
        "projects": [],
    }

    migrated = _migrate(config)

    assert migrated == config
    assert "api_token" not in migrated["credentials"]
    assert "email" not in migrated["credentials"]


def test_explicit_empty_legacy_fields_do_not_migrate() -> None:
    config = {
        "credentials": {
            "auth_type": "OAuth 2.0",
            "client_id": "id",
            "client_secret": "secret",
            "refresh_token": "rt",
        },
        "api_token": "",
        "email": "",
        "domain": "x.atlassian.net",
    }

    migrated = _migrate(config)

    assert migrated["credentials"] == config["credentials"]
    assert "api_token" not in migrated["credentials"]
    assert "email" not in migrated["credentials"]


def test_flat_legacy_config_migrates_fully() -> None:
    config = {
        "api_token": "tok",
        "email": "me@example.com",
        "domain": "x.atlassian.net",
    }

    migrated = _migrate(config)

    assert migrated["credentials"] == {
        "auth_type": "API Token",
        "api_token": "tok",
        "email": "me@example.com",
    }


def test_half_migrated_config_gets_missing_nested_field() -> None:
    config = {
        "credentials": {
            "auth_type": "API Token",
            "api_token": "tok",
        },
        "email": "me@example.com",
        "domain": "x.atlassian.net",
    }

    migrated = _migrate(config)

    assert migrated["credentials"]["email"] == "me@example.com"
    assert migrated["credentials"]["api_token"] == "tok"
    assert migrated["credentials"]["auth_type"] == "API Token"


def test_missing_domain_does_not_add_empty_domain() -> None:
    config = {
        "credentials": {
            "auth_type": "API Token",
            "api_token": "tok",
            "email": "me@example.com",
        }
    }

    migrated = _migrate(config)

    assert "domain" not in migrated


@pytest.mark.parametrize(
    ("domain", "expected"),
    [
        ("https://x.atlassian.net/", "x.atlassian.net"),
        ("http://x.atlassian.net", "x.atlassian.net"),
        ("x.atlassian.net/", "x.atlassian.net"),
        ("x.atlassian.net", "x.atlassian.net"),
    ],
)
def test_domain_protocol_and_trailing_slash_are_stripped(domain: str, expected: str) -> None:
    migrated = _migrate(
        {
            "credentials": {
                "auth_type": "API Token",
                "api_token": "tok",
                "email": "me@example.com",
            },
            "domain": domain,
        }
    )

    assert migrated["domain"] == expected
