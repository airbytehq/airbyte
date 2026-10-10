#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


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

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CALENDAR_LIST_URL = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


def test_legacy_flat_config_is_migrated_to_custom_app_option(capsys):
    source = get_source(LEGACY_CONFIG)

    assert source._config["credentials"] == MIGRATED_CREDENTIALS
    for key in ("client_id", "client_secret", "client_refresh_token_2"):
        assert key not in source._config
    assert source._config["calendarid"] == "primary"

    control_messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if '"CONTROL"' in line]
    assert len(control_messages) == 1
    assert control_messages[0]["type"] == Type.CONTROL.value
    emitted_config = control_messages[0]["control"]["connectorConfig"]["config"]
    assert emitted_config["credentials"] == MIGRATED_CREDENTIALS
    assert "client_refresh_token_2" not in emitted_config


@pytest.mark.parametrize("auth_type", ["manual", "oauth2.0"])
def test_nested_config_is_not_migrated(capsys, auth_type):
    config = {
        "credentials": {"auth_type": auth_type, "client_id": "id", "client_secret": "secret", "refresh_token": "rt"},
        "calendarid": "primary",
    }

    source = get_source(config)

    assert source._config == config
    assert "CONTROL" not in capsys.readouterr().out


def test_migrated_credentials_reach_the_token_endpoint(requests_mock):
    token_request = requests_mock.post(_TOKEN_URL, json={"access_token": "at", "expires_in": 3600})
    requests_mock.get(_CALENDAR_LIST_URL, json={"items": []})
    catalog = CatalogBuilder().with_stream("calendarlist", SyncMode.full_refresh).build()

    output = read(get_source(dict(LEGACY_CONFIG)), LEGACY_CONFIG, catalog)

    assert output.errors == []
    assert token_request.called
    body = token_request.last_request.text
    assert "refresh_token=legacy-refresh" in body
    assert "client_id=legacy-id.apps.googleusercontent.com" in body
    assert "grant_type=refresh_token" in body
    calendar_request = next(r for r in requests_mock.request_history if r.url.startswith(_CALENDAR_LIST_URL))
    assert calendar_request.headers["Authorization"] == "Bearer at"
