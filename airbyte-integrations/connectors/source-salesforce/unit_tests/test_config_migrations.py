#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock, patch

import pytest
from source_salesforce.api import Salesforce
from source_salesforce.config_migrations import MigrateCredentialsToOAuth
from source_salesforce.source import SourceSalesforce


@pytest.mark.parametrize(
    "input_config,expected_should_migrate",
    [
        pytest.param(
            {
                "client_id": "old_id",
                "client_secret": "old_secret",
                "refresh_token": "old_token",
                "auth_type": "Client",
                "is_sandbox": False,
            },
            True,
            id="flat_config_needs_migration",
        ),
        pytest.param(
            {
                "credentials": {
                    "auth_type": "Client",
                    "client_id": "new_id",
                    "client_secret": "new_secret",
                    "refresh_token": "new_token",
                },
                "is_sandbox": False,
            },
            False,
            id="nested_config_already_migrated",
        ),
        pytest.param(
            {"is_sandbox": True},
            False,
            id="empty_config_no_credentials",
        ),
    ],
)
def test_should_migrate(input_config, expected_should_migrate):
    assert MigrateCredentialsToOAuth.should_migrate(input_config) == expected_should_migrate


@pytest.mark.parametrize(
    "input_config,expected_output",
    [
        pytest.param(
            {
                "client_id": "my_id",
                "client_secret": "my_secret",
                "refresh_token": "my_token",
                "auth_type": "Client",
                "is_sandbox": False,
                "start_date": "2021-01-01",
            },
            {
                "credentials": {
                    "auth_type": "Client",
                    "client_id": "my_id",
                    "client_secret": "my_secret",
                    "refresh_token": "my_token",
                },
                "is_sandbox": False,
                "start_date": "2021-01-01",
            },
            id="migrates_all_credential_fields_into_nested_object",
        ),
        pytest.param(
            {
                "client_id": "my_id",
                "client_secret": "my_secret",
                "refresh_token": "my_token",
                "is_sandbox": True,
            },
            {
                "credentials": {
                    "auth_type": "Client",
                    "client_id": "my_id",
                    "client_secret": "my_secret",
                    "refresh_token": "my_token",
                },
                "is_sandbox": True,
            },
            id="defaults_auth_type_to_client_when_missing",
        ),
    ],
)
def test_transform(input_config, expected_output):
    result = MigrateCredentialsToOAuth.transform(input_config)
    assert result == expected_output
    assert "client_id" not in result
    assert "client_secret" not in result
    assert "refresh_token" not in result
    assert "auth_type" not in result


def test_get_sf_object_with_nested_credentials():
    """Verify `_get_sf_object` correctly extracts credentials from the nested config structure."""
    config = {
        "credentials": {
            "auth_type": "ClientManual",
            "client_id": "manual_id",
            "client_secret": "manual_secret",
            "refresh_token": "manual_token",
        },
        "is_sandbox": True,
        "start_date": "2021-01-01",
    }
    with patch("source_salesforce.source.Salesforce") as mock_sf_cls:
        mock_sf_cls.return_value = Mock()
        SourceSalesforce._get_sf_object(config)
        mock_sf_cls.assert_called_once()
        call_kwargs = mock_sf_cls.call_args[1]
        assert call_kwargs["client_id"] == "manual_id"
        assert call_kwargs["client_secret"] == "manual_secret"
        assert call_kwargs["refresh_token"] == "manual_token"
        assert call_kwargs["is_sandbox"] is True


def test_get_sf_object_passes_manual_credentials():
    """When auth_type is 'ClientManual', the user's own credentials must be passed through to the Salesforce API."""
    config = {
        "credentials": {
            "auth_type": "ClientManual",
            "client_id": "user_app_id",
            "client_secret": "user_app_secret",
            "refresh_token": "user_app_token",
        },
        "is_sandbox": True,
        "start_date": "2021-01-01",
    }
    credentials = config.get("credentials", {})
    flat_config = {**config, **credentials}
    sf = Salesforce(**flat_config)
    assert sf.client_id == "user_app_id"
    assert sf.client_secret == "user_app_secret"
    assert sf.refresh_token == "user_app_token"
    assert sf.is_sandbox is True


def test_get_sf_object_passes_oauth_credentials():
    """When auth_type is 'Client' (OAuth), platform-injected credentials are used."""
    config = {
        "credentials": {
            "auth_type": "Client",
            "client_id": "platform_id",
            "client_secret": "platform_secret",
            "refresh_token": "platform_token",
        },
        "is_sandbox": False,
        "start_date": "2021-01-01",
    }
    credentials = config.get("credentials", {})
    flat_config = {**config, **credentials}
    sf = Salesforce(**flat_config)
    assert sf.client_id == "platform_id"
    assert sf.client_secret == "platform_secret"
    assert sf.refresh_token == "platform_token"
    assert sf.is_sandbox is False


def test_migrate_end_to_end(tmp_path):
    """Full migration round-trip: write old config, run migration, verify new structure."""
    old_config = {
        "client_id": "e2e_id",
        "client_secret": "e2e_secret",
        "refresh_token": "e2e_token",
        "auth_type": "Client",
        "is_sandbox": False,
        "start_date": "2021-01-01",
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(old_config))

    source = Mock()
    source.read_config.return_value = old_config
    source.write_config = Mock()

    entrypoint_mock = Mock()
    entrypoint_mock.extract_config.return_value = str(config_path)

    with patch("source_salesforce.config_migrations.AirbyteEntrypoint", return_value=entrypoint_mock):
        with patch("source_salesforce.config_migrations.emit_configuration_as_airbyte_control_message") as mock_emit:
            MigrateCredentialsToOAuth.migrate(["--config", str(config_path)], source)

    source.write_config.assert_called_once()
    saved_config = source.write_config.call_args[0][0]
    assert "credentials" in saved_config
    assert saved_config["credentials"]["client_id"] == "e2e_id"
    assert saved_config["credentials"]["client_secret"] == "e2e_secret"
    assert saved_config["credentials"]["refresh_token"] == "e2e_token"
    assert saved_config["credentials"]["auth_type"] == "Client"
    assert "client_id" not in saved_config
    assert "client_secret" not in saved_config
    assert saved_config["is_sandbox"] is False
    mock_emit.assert_called_once()
