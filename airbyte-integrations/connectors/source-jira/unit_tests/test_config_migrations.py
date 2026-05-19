# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


CLOUD_ID = "12345678-1234-1234-1234-123456789abc"

_TENANT_INFO_RESPONSE = json.dumps({"cloudId": CLOUD_ID}).encode()


def _mock_tenant_info():
    resp = MagicMock()
    resp.read.return_value = _TENANT_INFO_RESPONSE
    resp.__enter__ = lambda s: BytesIO(_TENANT_INFO_RESPONSE)
    resp.__exit__ = lambda s, *a: None
    return patch("components.urllib.request.urlopen", return_value=resp)


def _migrated_config(config):
    source = YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH))
    return source._config


@pytest.mark.parametrize(
    "config, expected_domain",
    [
        pytest.param(
            {
                "credentials": {
                    "auth_type": "API Token",
                    "api_token": "token",
                    "email": "email@email.com",
                },
                "domain": "airbyteio.atlassian.net",
            },
            "airbyteio.atlassian.net",
            id="api_token_nested_credentials",
        ),
        pytest.param(
            {
                "api_token": "token",
                "email": "email@email.com",
                "domain": "https://airbyteio.atlassian.net/",
            },
            "airbyteio.atlassian.net",
            id="legacy_flat_credentials_normalized_domain",
        ),
        pytest.param(
            {
                "credentials": {
                    "auth_type": "API Token",
                    "api_token": "token",
                    "email": "email@email.com",
                    "domain": "airbyteio.jira.com",
                },
                "domain": "airbyteio.atlassian.net",
            },
            "airbyteio.jira.com",
            id="nested_domain_takes_precedence",
        ),
    ],
)
def test_config_migrations_copy_root_domain_to_api_token_credentials(config, expected_domain):
    migrated_config = _migrated_config(deepcopy(config))

    assert migrated_config["credentials"]["domain"] == expected_domain


def test_config_migrations_service_account_does_not_copy_root_domain():
    """Service Account has its own domain field — root domain migration should not overwrite it."""
    config = {
        "credentials": {
            "auth_type": "Service Account",
            "service_account_token": "token",
            "domain": "airbyteio.atlassian.net",
        },
        "domain": "other-site.atlassian.net",
    }
    with _mock_tenant_info():
        migrated_config = _migrated_config(deepcopy(config))

    assert migrated_config["credentials"]["domain"] == "airbyteio.atlassian.net"


def test_config_migrations_oauth_does_not_copy_root_domain():
    """OAuth credentials should not receive the root-level domain."""
    config = {
        "credentials": {
            "auth_type": "OAuth2.0",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "refresh_token": "refresh-token",
            "cloud_id": CLOUD_ID,
        },
        "domain": "airbyteio.atlassian.net",
    }
    migrated_config = _migrated_config(deepcopy(config))

    creds = migrated_config["credentials"]
    assert creds.get("domain") is None or "domain" not in creds
