#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, List, Mapping

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


LEGACY_CONFIG = {
    "client_id": "legacy-id.apps.googleusercontent.com",
    "client_secret": "legacy-secret",
    "client_refresh_token_2": "legacy-refresh",
    "calendarid": "primary",
}
MIGRATED_CREDENTIALS = {
    "auth_type": "manual",
    "client_id": "legacy-id.apps.googleusercontent.com",
    "client_secret": "legacy-secret",
    "refresh_token": "legacy-refresh",
}
FLAT_KEYS = ("client_id", "client_secret", "client_refresh_token_2")

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CALENDAR_LIST_URL = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


def _control_messages(capsys) -> List[Mapping[str, Any]]:
    return [json.loads(line) for line in capsys.readouterr().out.splitlines() if '"CONTROL"' in line]


def _assert_valid_against_spec(source) -> None:
    check_config_against_spec_or_exit(source._config, source.spec(logging.getLogger("test")))


def test_legacy_flat_config_is_migrated_to_custom_app_option(capsys):
    source = get_source(LEGACY_CONFIG)

    assert source._config["credentials"] == MIGRATED_CREDENTIALS
    for key in FLAT_KEYS:
        assert key not in source._config
    assert source._config["calendarid"] == "primary"
    _assert_valid_against_spec(source)

    control_messages = _control_messages(capsys)
    assert len(control_messages) == 1
    assert control_messages[0]["type"] == Type.CONTROL.value
    emitted_config = control_messages[0]["control"]["connectorConfig"]["config"]
    assert emitted_config["credentials"] == MIGRATED_CREDENTIALS
    assert "client_refresh_token_2" not in emitted_config


def test_legacy_values_stay_strings():
    # Without value_type the CDK would literal-eval these into int, bool, and float.
    source = get_source({"client_id": "123456", "client_secret": "True", "client_refresh_token_2": "1e5"})

    assert source._config["credentials"] == {"auth_type": "manual", "client_id": "123456", "client_secret": "True", "refresh_token": "1e5"}
    _assert_valid_against_spec(source)


@pytest.mark.parametrize("auth_type", ["manual", "oauth2.0"])
def test_nested_config_is_not_migrated(capsys, auth_type):
    config = {
        "credentials": {"auth_type": auth_type, "client_id": "id", "client_secret": "secret", "refresh_token": "rt"},
        "calendarid": "primary",
    }

    source = get_source(config)

    assert source._config == config
    assert _control_messages(capsys) == []
    _assert_valid_against_spec(source)


@pytest.mark.parametrize("auth_type", ["manual", "oauth2.0"])
def test_existing_credentials_are_kept_when_flat_keys_remain(capsys, auth_type):
    # A partial update through the public API merges a new `credentials` block into a flat config
    # that has not been migrated yet, so both shapes can be present at once.
    credentials = {"auth_type": auth_type, "client_id": "new-id", "client_secret": "new-secret", "refresh_token": "new-refresh"}
    config = {**LEGACY_CONFIG, "credentials": dict(credentials)}

    source = get_source(config)

    assert source._config["credentials"] == credentials
    for key in FLAT_KEYS:
        assert key not in source._config

    control_messages = _control_messages(capsys)
    assert len(control_messages) == 1
    assert control_messages[0]["control"]["connectorConfig"]["config"]["credentials"] == credentials


@pytest.mark.parametrize(
    "config",
    [
        pytest.param({k: v for k, v in LEGACY_CONFIG.items() if k != "client_id"}, id="flat_without_client_id"),
        pytest.param({k: v for k, v in LEGACY_CONFIG.items() if k != "client_secret"}, id="flat_without_client_secret"),
        pytest.param({k: v for k, v in LEGACY_CONFIG.items() if k != "client_refresh_token_2"}, id="flat_without_refresh_token"),
        pytest.param({**LEGACY_CONFIG, "credentials": None}, id="credentials_null"),
        pytest.param({**LEGACY_CONFIG, "credentials": {"refresh_token": "new-refresh"}}, id="flat_plus_refresh_token_only"),
    ],
)
def test_incomplete_config_is_left_for_spec_validation(capsys, config):
    # Nothing is migrated or removed, so no stored value is lost, and spec validation reports the problem.
    source = get_source(json.loads(json.dumps(config)))

    assert source._config == config
    assert _control_messages(capsys) == []
    with pytest.raises(AirbyteTracedException):
        _assert_valid_against_spec(source)


@pytest.mark.parametrize(
    "config",
    [
        pytest.param({**LEGACY_CONFIG, "credentials": {"client_secret": "s", "refresh_token": "r"}}, id="no_client_id"),
        pytest.param({**LEGACY_CONFIG, "credentials": {"client_id": "i", "refresh_token": "r"}}, id="no_client_secret"),
        pytest.param(
            {"client_secret": "x", "client_refresh_token_2": "y", "credentials": {"client_id": "i", "client_secret": "s"}},
            id="no_refresh_token",
        ),
    ],
)
def test_flat_keys_kept_while_credentials_lack_one_field(config):
    # Each case lacks exactly one `credentials` field, so every clause of the remove condition is exercised on its own.
    assert get_source(json.loads(json.dumps(config)))._config == config


def test_advanced_auth_targets_the_oauth_option():
    spec = get_source(dict(LEGACY_CONFIG)).spec(logging.getLogger("test"))
    oauth = spec.advanced_auth
    credentials = spec.connectionSpecification["properties"]["credentials"]
    oauth_option = next(o for o in credentials["oneOf"] if o["properties"]["auth_type"]["const"] == "oauth2.0")

    assert oauth.auth_flow_type.value == "oauth2.0"
    assert oauth.predicate_key == ["credentials", "auth_type"]
    assert oauth.predicate_value == oauth_option["properties"]["auth_type"]["const"]
    config_spec = oauth.oauth_config_specification
    outputs = {
        **config_spec.complete_oauth_output_specification["properties"],
        **config_spec.complete_oauth_server_output_specification["properties"],
    }
    assert {name: field["path_in_connector_config"] for name, field in outputs.items()} == {
        "refresh_token": ["credentials", "refresh_token"],
        "client_id": ["credentials", "client_id"],
        "client_secret": ["credentials", "client_secret"],
    }
    for name in outputs:
        assert name in oauth_option["properties"]
        assert name in oauth_option["required"]


@pytest.mark.parametrize(
    "config, client_id, client_secret, refresh_token",
    [
        pytest.param(LEGACY_CONFIG, "legacy-id.apps.googleusercontent.com", "legacy-secret", "legacy-refresh", id="legacy_flat"),
        pytest.param(
            {"credentials": {"auth_type": "oauth2.0", "client_id": "app-id", "client_secret": "app-secret", "refresh_token": "oauth-rt"}},
            "app-id",
            "app-secret",
            "oauth-rt",
            id="nested_oauth",
        ),
        pytest.param(
            {"credentials": {"auth_type": "manual", "client_id": "own-id", "client_secret": "own-secret", "refresh_token": "own-rt"}},
            "own-id",
            "own-secret",
            "own-rt",
            id="nested_manual",
        ),
    ],
)
def test_credentials_reach_the_token_endpoint(config, client_id, client_secret, refresh_token):
    catalog = CatalogBuilder().with_stream("calendarlist", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        token_request = HttpRequest(
            _TOKEN_URL,
            body=f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}",
        )
        http_mocker.post(token_request, HttpResponse(json.dumps({"access_token": "at", "expires_in": 3600})))
        calendar_list_request = HttpRequest(
            _CALENDAR_LIST_URL, headers={"Authorization": "Bearer at"}, query_params={"maxResults": "250", "showDeleted": "true"}
        )
        http_mocker.get(calendar_list_request, HttpResponse(json.dumps({"items": [{"id": "primary"}]})))

        output = read(get_source(dict(config)), dict(config), catalog)

        assert output.errors == []
        assert [r.record.data["id"] for r in output.records] == ["primary"]
        http_mocker.assert_number_of_calls(token_request, 1)
