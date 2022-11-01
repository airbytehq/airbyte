import base64
import json
import re
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock
from ci_credentials.main import ENV_GCP_GSM_CREDENTIALS
from ci_credentials.main import main

from ci_credentials import SecretsLoader

HERE = Path(__file__).resolve().parent
TEST_CONNECTOR_NAME = "source-test"
TEMP_FOLDER = Path(tempfile.mkdtemp())


@pytest.fixture(autouse=True, scope="session")
def temp_folder():
    yield
    shutil.rmtree(TEMP_FOLDER)


@pytest.mark.parametrize(
    "connector_name,filename,expected_name",
    (
            ("source-default", "config.json", "SECRET_SOURCE-DEFAULT__CREDS"),
            ("source-custom-filename-1", "config_custom.json", "SECRET_SOURCE-CUSTOM-FILENAME-1_CUSTOM__CREDS"),
            ("source-custom-filename-2", "auth.json", "SECRET_SOURCE-CUSTOM-FILENAME-2_AUTH__CREDS"),
            ("source-custom-filename-3", "config_auth-test---___---config.json",
             "SECRET_SOURCE-CUSTOM-FILENAME-3_AUTH-TEST__CREDS"),
            ("source-custom-filename-4", "_____config_test---config.json",
             "SECRET_SOURCE-CUSTOM-FILENAME-4_TEST__CREDS"),
    )
)
def test_secret_name_generation(connector_name, filename, expected_name):
    assert SecretsLoader.generate_secret_name(connector_name, filename) == expected_name


def read_last_log_message(capfd):
    _, err = capfd.readouterr()
    print(err)
    return err.split("# ")[-1].strip()


def test_main(capfd, monkeypatch):
    # without parameters and envs
    monkeypatch.delenv(ENV_GCP_GSM_CREDENTIALS, raising=False)
    monkeypatch.setattr("sys.argv", [None, TEST_CONNECTOR_NAME, "fake_arg"])
    assert main() == 1
    assert "one script argument only" in read_last_log_message(capfd)

    monkeypatch.setattr("sys.argv", [None, TEST_CONNECTOR_NAME])
    # without env values
    assert main() == 1
    assert "shouldn't be empty" in read_last_log_message(capfd)

    # incorrect GCP_GSM_CREDENTIALS
    monkeypatch.setenv(ENV_GCP_GSM_CREDENTIALS, "non-json")
    assert main() == 1
    assert "incorrect GCP_GSM_CREDENTIALS value" in read_last_log_message(capfd)

    # empty GCP_GSM_CREDENTIALS
    monkeypatch.setenv(ENV_GCP_GSM_CREDENTIALS, "{}")
    assert main() == 1
    assert "GCP_GSM_CREDENTIALS shouldn't be empty!" in read_last_log_message(capfd)

    # successful result
    monkeypatch.setenv(ENV_GCP_GSM_CREDENTIALS, '{"test": "test"}')

    monkeypatch.setattr(SecretsLoader, "read_from_gsm", lambda *args, **kwargs: {})
    monkeypatch.setattr(SecretsLoader, "write_to_storage", lambda *args, **kwargs: 0)
    assert main() == 0


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
                        ("config.json", {"test_key": "test_value"}),
                        ("config_oauth.json", {"test_key_1": "test_key_2"}),
                    ]
            ),
    ),
    ids=["gsm_only", ]

)
@patch('ci_common_utils.GoogleApi.get_access_token', lambda *args: ("fake_token", None))
@patch('ci_common_utils.GoogleApi.project_id', "fake_id")
def test_read(connector_name, gsm_secrets, expected_secrets):
    matcher_gsm_list = re.compile("https://secretmanager.googleapis.com/v1/projects/.+/secrets")
    secrets_list = {"secrets": [{
        "name": f"projects/<fake_id>/secrets/SECRET_{connector_name.upper()}_{i}_CREDS",
        "labels": {
            "filename": k,
            "connector": connector_name,
        }
    } for i, k in enumerate(gsm_secrets)]}

    matcher_versions = re.compile("https://secretmanager.googleapis.com/v1/.+/versions")
    versions_response_list = [{"json": {
        "versions": [{
            "name": f"projects/<fake_id>/secrets/SECRET_{connector_name.upper()}_{i}_CREDS/versions/1",
            "state": "ENABLED",
        }]
    }} for i in range(len(gsm_secrets))]

    matcher_secret = re.compile("https://secretmanager.googleapis.com/v1/.+/1:access")
    secrets_response_list = [{
        "json": {"payload": {"data": base64.b64encode(json.dumps(v).encode()).decode("utf-8")}}
    } for v in gsm_secrets.values()]

    matcher_version = re.compile("https://secretmanager.googleapis.com/v1/.+:addVersion")
    loader = SecretsLoader(connector_name=connector_name, gsm_credentials={})
    with requests_mock.Mocker() as m:
        m.get(matcher_gsm_list, json=secrets_list)
        m.post(matcher_gsm_list, json={"name": "<fake_name>"})
        m.post(matcher_version, json={})
        m.get(matcher_versions, versions_response_list)
        m.get(matcher_secret, secrets_response_list)

        secrets = [(*k, v.replace(" ", "")) for k, v in loader.read_from_gsm().items()]
        expected_secrets = [(connector_name, k[0], json.dumps(k[1]).replace(" ", "")) for k in expected_secrets]
        # raise Exception("%s => %s" % (secrets, expected_secrets))
        # raise Exception(set(secrets).symmetric_difference(set(expected_secrets)))
        assert not set(secrets).symmetric_difference(set(expected_secrets))


@pytest.mark.parametrize(
    "connector_name,secrets,expected_files",
    (
            ("source-test", {"test.json": "test_value"},
             ["airbyte-integrations/connectors/source-test/secrets/test.json"]),

            ("source-test2", {"test.json": "test_value", "auth.json": "test_auth"},
             ["airbyte-integrations/connectors/source-test2/secrets/test.json",
              "airbyte-integrations/connectors/source-test2/secrets/auth.json"]),

            ("base-normalization", {"test.json": "test_value", "auth.json": "test_auth"},
             ["airbyte-integrations/bases/base-normalization/secrets/test.json",
              "airbyte-integrations/bases/base-normalization/secrets/auth.json"]),
    ),
    ids=["single", "multi", "base-normalization"],
)
def test_write(connector_name, secrets, expected_files):
    loader = SecretsLoader(connector_name=connector_name, gsm_credentials={})
    loader.base_folder = TEMP_FOLDER
    loader.write_to_storage({(connector_name, k): v for k, v in secrets.items()})
    for expected_file in expected_files:
        target_file = TEMP_FOLDER / expected_file
        assert target_file.exists()
        has = False
        for k, v in secrets.items():
            if target_file.name == k:
                with open(target_file, "r") as f:
                    assert f.read() == v
                has = True
                break
        assert has, f"incorrect file data: {target_file}"


@pytest.mark.parametrize(
    "connector_name,dict_json_value,expected_secret",
    (
            ("source-default", "{\"org_id\": 111}", "::add-mask::111"),
            ("source-default", "{\"org\": 111}", ""),
    )
)
def test_validate_mask_values(connector_name, dict_json_value, expected_secret, capsys):
    loader = SecretsLoader(connector_name=connector_name, gsm_credentials={})
    json_value = json.loads(dict_json_value)
    loader.mask_secrets_from_action_log(None, json_value)
    assert expected_secret in capsys.readouterr().out
