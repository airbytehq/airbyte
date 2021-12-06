import pytest
from ci_credentials.main import ENV_GITHUB_PROVIDED_SECRETS_JSON, ENV_GCP_GSM_CREDENTIALS
from ci_credentials.main import main

from ci_credentials import SecretsLoader

TEST_CONNECTOR_NAME = "source-test-something"


@pytest.mark.parametrize(
    "connector_name,filename,expected_name",
    (
            ("source-default", "config.json", "SECRET_SOURCE-DEFAULT_CREDS"),
            ("source-custom-filename-1", "config_custom.json", "SECRET_SOURCE-CUSTOM-FILENAME-1_CUSTOM_CREDS"),
            ("source-custom-filename-2", "auth.json", "SECRET_SOURCE-CUSTOM-FILENAME-2_AUTH_CREDS"),
            ("source-custom-filename-3", "config_auth-test---___---config.json",
             "SECRET_SOURCE-CUSTOM-FILENAME-3_AUTH-TEST_CREDS"),
            ("source-custom-filename-4", "_____config_test---config.json",
             "SECRET_SOURCE-CUSTOM-FILENAME-4_TEST_CREDS"),
    )
)
def test_secret_name_generation(connector_name, filename, expected_name):
    assert SecretsLoader.generate_secret_name(connector_name, filename) == expected_name


def read_last_log_message(capfd):
    _, err = capfd.readouterr()
    return err.split("# ")[-1].strip()


def test_main(capfd, monkeypatch):
    # without parameters and envs
    monkeypatch.delenv(ENV_GITHUB_PROVIDED_SECRETS_JSON, raising=False)
    monkeypatch.delenv(ENV_GCP_GSM_CREDENTIALS, raising=False)
    assert main() == 1
    assert "one script argument only" in read_last_log_message(capfd)

    monkeypatch.setattr("sys.argv", [None, TEST_CONNECTOR_NAME])
    # without envs
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

    # incorrect GITHUB_PROVIDED_SECRETS_JSON
    monkeypatch.setenv(ENV_GITHUB_PROVIDED_SECRETS_JSON, "non-json")
    assert main() == 1
    assert "incorrect GITHUB_PROVIDED_SECRETS_JSON value" in read_last_log_message(capfd)

    # successful result
    monkeypatch.setenv(ENV_GCP_GSM_CREDENTIALS, '{"test": "test"}')
    monkeypatch.setenv(ENV_GITHUB_PROVIDED_SECRETS_JSON, "{}")

    monkeypatch.setattr(SecretsLoader, "read", lambda *args, **kwargs: {})
    monkeypatch.setattr(SecretsLoader, "write", lambda *args, **kwargs: 0)
    assert main() == 0

# @pytest.mark.parametrize(
#     "gsm_data,github_data",
#     (
#             ("source-default", "config.json", "SECRET_SOURCE-DEFAULT_CREDS"),
#             ("source-custom-filename-1", "config_custom.json", "SECRET_SOURCE-CUSTOM-FILENAME-1_CUSTOM_CREDS"),
#             ("source-custom-filename-2", "auth.json", "SECRET_SOURCE-CUSTOM-FILENAME-2_AUTH_CREDS"),
#             ("source-custom-filename-3", "config_auth-test---___---config.json",
#              "SECRET_SOURCE-CUSTOM-FILENAME-3_AUTH-TEST_CREDS"),
#             ("source-custom-filename-4", "_____config_test---config.json",
#              "SECRET_SOURCE-CUSTOM-FILENAME-4_TEST_CREDS"),
#     )
# )
# def test_read(gsm_data, github_data):
#     loader = SecretsLoader(
#         connector_name=TEST_CONNECTOR_NAME,
#         gsm_credentials=gsm_credentials,
#         github_secrets=github_secrets
#     )
