# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy

import pytest
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


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


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            {
                "credentials": {
                    "auth_type": "Service Account",
                    "service_account_token": "token",
                    "cloud_id": "12345678-1234-1234-1234-123456789abc",
                },
                "domain": "airbyteio.atlassian.net",
            },
            id="service_account_ignores_root_domain",
        ),
        pytest.param(
            {
                "credentials": {
                    "auth_type": "OAuth2.0",
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                    "refresh_token": "refresh-token",
                    "cloud_id": "12345678-1234-1234-1234-123456789abc",
                },
                "domain": "airbyteio.atlassian.net",
            },
            id="oauth_ignores_root_domain",
        ),
    ],
)
def test_config_migrations_do_not_copy_root_domain_to_gateway_auth_credentials(config):
    migrated_config = _migrated_config(deepcopy(config))

    assert "domain" not in migrated_config["credentials"]
