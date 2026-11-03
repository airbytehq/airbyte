# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
import logging
from pathlib import Path

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_COMPANY_URL = "https://api.aircall.io/v1/company"
_COMPANY_RESPONSE = HttpResponse(body=json.dumps({"company": {"name": "Airbyte"}}), status_code=200)
_LEGACY_CONFIG = {
    "api_id": "0123456789",
    "api_token": "legacy-token",
    "start_date": "2022-03-01T00:00:00.000Z",
}
_API_KEY_CONFIG = {
    "credentials": {"auth_type": "api_key", "api_id": "test-id", "api_token": "test-token"},
}
_OAUTH_CONFIG = {
    "credentials": {
        "auth_type": "oauth2.0",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "access_token": "oauth-access-token",
    },
}


def _manifest() -> dict:
    return yaml.safe_load(_YAML_FILE_PATH.read_text())


def _basic(api_id: str, api_token: str) -> str:
    return "Basic " + base64.b64encode(f"{api_id}:{api_token}".encode()).decode()


def _check_with_authorization(config: dict, authorization: str) -> None:
    request = HttpRequest(_COMPANY_URL, headers={"Authorization": authorization})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _COMPANY_RESPONSE)

        status = get_source(config=config).check(logging.getLogger("aircall-test"), config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(request, 1)


def test_spec_offers_oauth_first_then_api_key() -> None:
    connection_specification = _manifest()["spec"]["connection_specification"]
    options = connection_specification["properties"]["credentials"]["oneOf"]

    assert connection_specification["required"] == ["credentials"]
    assert "api_id" not in connection_specification["properties"]
    assert "api_token" not in connection_specification["properties"]
    assert [option["properties"]["auth_type"]["const"] for option in options] == ["oauth2.0", "api_key"]
    assert options[0]["required"] == ["auth_type", "client_id", "client_secret", "access_token"]
    assert options[1]["required"] == ["auth_type", "api_id", "api_token"]
    for option, secrets in zip(options, (("client_id", "client_secret", "access_token"), ("api_id", "api_token"))):
        assert all(option["properties"][name]["airbyte_secret"] for name in secrets)


def test_advanced_auth_uses_aircall_declarative_oauth_with_access_token_only() -> None:
    advanced_auth = _manifest()["spec"]["advanced_auth"]
    oauth_spec = advanced_auth["oauth_config_specification"]
    connector_input = oauth_spec["oauth_connector_input_specification"]

    assert advanced_auth["auth_flow_type"] == "oauth2.0"
    assert advanced_auth["predicate_key"] == ["credentials", "auth_type"]
    assert advanced_auth["predicate_value"] == "oauth2.0"
    assert connector_input["consent_url"] == (
        "https://dashboard.aircall.io/oauth/authorize?{{client_id_param}}&{{redirect_uri_param}}"
        "&response_type=code&{{scope_param}}&{{state_param}}"
    )
    assert connector_input["scope"] == "public_api"
    assert connector_input["access_token_url"] == "https://api.aircall.io/v1/oauth/token"
    assert connector_input["access_token_headers"] == {"Content-Type": "application/json"}
    assert connector_input["access_token_params"] == {
        "client_id": "{{ client_id_value }}",
        "client_secret": "{{ client_secret_value }}",
        "code": "{{ auth_code_value }}",
        "redirect_uri": "{{ redirect_uri_value }}",
        "grant_type": "authorization_code",
    }
    assert connector_input["extract_output"] == ["access_token"]
    assert oauth_spec["complete_oauth_output_specification"]["properties"] == {
        "access_token": {"type": "string", "path_in_connector_config": ["credentials", "access_token"]},
    }
    server_output = oauth_spec["complete_oauth_server_output_specification"]["properties"]
    assert {name: value["path_in_connector_config"] for name, value in server_output.items()} == {
        "client_id": ["credentials", "client_id"],
        "client_secret": ["credentials", "client_secret"],
    }


def test_legacy_api_key_config_migrates_into_credentials() -> None:
    source = get_source(config=dict(_LEGACY_CONFIG))

    assert source._config == {
        "start_date": "2022-03-01T00:00:00.000Z",
        "credentials": {"auth_type": "api_key", "api_id": "0123456789", "api_token": "legacy-token"},
    }


def test_legacy_api_key_migration_is_persisted_to_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(_LEGACY_CONFIG))

    get_source(config=dict(_LEGACY_CONFIG), config_path=str(config_path))

    assert json.loads(config_path.read_text()) == {
        "start_date": "2022-03-01T00:00:00.000Z",
        "credentials": {"auth_type": "api_key", "api_id": "0123456789", "api_token": "legacy-token"},
    }


@pytest.mark.parametrize("config", [_API_KEY_CONFIG, _OAUTH_CONFIG], ids=["api_key", "oauth"])
def test_credentials_configs_are_not_migrated(config: dict, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

    source = get_source(config=json.loads(json.dumps(config)), config_path=str(config_path))

    assert source._config == config
    assert json.loads(config_path.read_text()) == config


def test_legacy_api_key_config_authenticates_with_basic_auth() -> None:
    _check_with_authorization(dict(_LEGACY_CONFIG), _basic("0123456789", "legacy-token"))


def test_api_key_credentials_authenticate_with_basic_auth() -> None:
    _check_with_authorization(_API_KEY_CONFIG, _basic("test-id", "test-token"))


def test_oauth_credentials_authenticate_with_bearer_access_token() -> None:
    _check_with_authorization(_OAUTH_CONFIG, "Bearer oauth-access-token")
