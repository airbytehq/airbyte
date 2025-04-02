#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import json
import re
from unittest.mock import patch

import pytest
import requests_mock
from ci_credentials import SecretsManager
from ci_credentials.models import RemoteSecret, Secret


@pytest.fixture
def matchers():
    return {
        "secrets": re.compile("https://secretmanager.googleapis.com/v1/projects/.+/secrets"),
        "versions": re.compile("https://secretmanager.googleapis.com/v1/.+/versions"),
        "addVersion": re.compile("https://secretmanager.googleapis.com/v1/.+:addVersion"),
        "access": re.compile("https://secretmanager.googleapis.com/v1/.+/1:access"),
        "disable": re.compile("https://secretmanager.googleapis.com/v1/.+:disable"),
        "spec_secret_mask": re.compile("https://connectors.airbyte.com/files/registries/v0/specs_secrets_mask.yaml"),
    }


@pytest.mark.parametrize(
    "connector_name,gsm_secrets,expected_secrets",
    (
        (
            "source-gsm-only",
            {
                "config": {"test_key": "test_value"},
                "config_oauth": {"test_key_1": "test_key_2"},
            },
            [
                RemoteSecret(
                    "source-gsm-only",
                    "config.json",
                    '{"test_key":"test_value"}',
                    "projects/<fake_id>/secrets/SECRET_SOURCE-GSM-ONLY_0_CREDS/versions/1",
                ),
                RemoteSecret(
                    "source-gsm-only",
                    "config_oauth.json",
                    '{"test_key_1":"test_key_2"}',
                    "projects/<fake_id>/secrets/SECRET_SOURCE-GSM-ONLY_1_CREDS/versions/1",
                ),
            ],
        ),
    ),
    ids=[
        "gsm_only",
    ],
)
@patch("ci_credentials.google_api.GoogleApi.get_access_token", lambda *args: ("fake_token", None))
@patch("ci_credentials.google_api.GoogleApi.project_id", "fake_id")
def test_read(matchers, connector_name, gsm_secrets, expected_secrets):
    secrets_list = {
        "secrets": [
            {
                "name": f"projects/<fake_id>/secrets/SECRET_{connector_name.upper()}_{i}_CREDS",
                "labels": {
                    "filename": k,
                    "connector": connector_name,
                },
            }
            for i, k in enumerate(gsm_secrets)
        ]
    }

    versions_response_list = [
        {
            "json": {
                "versions": [
                    {
                        "name": f"projects/<fake_id>/secrets/SECRET_{connector_name.upper()}_{i}_CREDS/versions/1",
                        "state": "ENABLED",
                    }
                ]
            }
        }
        for i in range(len(gsm_secrets))
    ]

    secrets_response_list = [
        {"json": {"payload": {"data": base64.b64encode(json.dumps(v).encode()).decode("utf-8")}}} for v in gsm_secrets.values()
    ]

    manager = SecretsManager(connector_name=connector_name, gsm_credentials={})
    with requests_mock.Mocker() as m:
        m.get(matchers["secrets"], json=secrets_list)
        m.post(matchers["secrets"], json={"name": "<fake_name>"})
        m.get(matchers["versions"], versions_response_list)
        m.get(matchers["access"], secrets_response_list)
        m.get(matchers["spec_secret_mask"], json={"spec_secret_mask": "test"})

        secrets = manager.read_from_gsm()
        assert secrets == expected_secrets


@pytest.mark.parametrize(
    "connector_name,secrets,expected_files",
    (
        (
            "source-test",
            [Secret("source-test", "test_config.json", "test_value")],
            ["airbyte-integrations/connectors/source-test/secrets/test_config.json"],
        ),
        (
            "source-test2",
            [Secret("source-test2", "test.json", "test_value"), Secret("source-test2", "auth.json", "test_auth")],
            [
                "airbyte-integrations/connectors/source-test2/secrets/test.json",
                "airbyte-integrations/connectors/source-test2/secrets/auth.json",
            ],
        ),
        (
            "base-normalization",
            [Secret("base-normalization", "test.json", "test_value"), Secret("base-normalization", "auth.json", "test_auth")],
            [
                "airbyte-integrations/bases/base-normalization/secrets/test.json",
                "airbyte-integrations/bases/base-normalization/secrets/auth.json",
            ],
        ),
        (
            "source-no-secret",
            [],
            [],
        ),
    ),
)
def test_write(tmp_path, connector_name, secrets, expected_files):
    manager = SecretsManager(connector_name=connector_name, gsm_credentials={})
    manager.base_folder = tmp_path
    written_files = manager.write_to_storage(secrets)
    for expected_file in expected_files:
        target_file = tmp_path / expected_file
        assert target_file.exists()
        assert target_file in written_files
        has = False
        for secret in secrets:
            if target_file.name == secret.configuration_file_name:
                with open(target_file, "r") as f:
                    assert f.read() == secret.value
                has = True
                break
        assert has, f"incorrect file data: {target_file}"


@pytest.mark.parametrize(
    "connector_name,dict_json_value,expected_secret",
    (
        ("source-default", '{"org_id": 111}', "::add-mask::111"),
        ("source-default", '{"org": 111}', ""),
    ),
)
def test_validate_mask_values(connector_name, dict_json_value, expected_secret, capsys):
    manager = SecretsManager(connector_name=connector_name, gsm_credentials={})
    json_value = json.loads(dict_json_value)
    manager.mask_secrets_from_action_log(None, json_value)
    assert expected_secret in capsys.readouterr().out


@patch("ci_credentials.google_api.GoogleApi.get_access_token", lambda *args: ("fake_token", None))
@patch("ci_credentials.google_api.GoogleApi.project_id", "fake_id")
@pytest.mark.parametrize(
    "old_secret_value, updated_configurations",
    [
        (json.dumps({"key": "value"}), [json.dumps({"key": "new_value_1"}), json.dumps({"key": "new_value_2"})]),
        (json.dumps({"key": "value"}), [json.dumps({"key": "value"})]),
    ],
)
def test_update_secrets(tmp_path, matchers, old_secret_value, updated_configurations):
    existing_secret = RemoteSecret("source-test", "config.json", old_secret_value, "previous_version")
    existing_secrets = [existing_secret]

    manager = SecretsManager(connector_name="source-test", gsm_credentials={})
    manager.base_folder = tmp_path
    updated_configuration_directory = tmp_path / "airbyte-integrations/connectors/source-test/secrets/updated_configurations"
    updated_configuration_directory.mkdir(parents=True)

    for i, updated_configuration in enumerate(updated_configurations):
        stem, ext = existing_secret.configuration_file_name.split(".")
        updated_configuration_file_name = f"{stem}|{i}.{ext}"
        updated_configuration_path = updated_configuration_directory / updated_configuration_file_name
        with open(updated_configuration_path, "w") as f:
            f.write(updated_configuration)

    with requests_mock.Mocker() as m:
        add_version_adapter = m.post(matchers["addVersion"], json={"name": "new_version"})
        disable_version_adapter = m.post(matchers["disable"], json={})
        updated_secrets = manager.update_secrets(existing_secrets)

    if old_secret_value != updated_configurations[-1]:
        # We confirm the new version was created from the latest updated_configuration value
        for secret in updated_secrets:
            assert secret.connector_name == "source-test"
            assert secret.configuration_file_name == "config.json"
            assert secret.value == updated_configurations[-1]
            assert secret.enabled_version == "new_version"
        expected_add_version_payload = {"payload": {"data": base64.b64encode(updated_configurations[-1].encode()).decode("utf-8")}}
        assert add_version_adapter.last_request.json() == expected_add_version_payload
        assert disable_version_adapter.called_once
    else:
        assert not updated_secrets
        assert not add_version_adapter.called
        assert not disable_version_adapter.called
