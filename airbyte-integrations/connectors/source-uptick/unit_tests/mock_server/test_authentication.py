# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server coverage for the `SelectiveAuthenticator` on `credentials.auth_type`.

Three shapes reach the connector:
  - legacy top-level `client_id`/`client_secret`/`username`/`password` — `config_normalization_rules`
    moves them under `credentials` with `auth_type: password` in memory (no CONTROL message), so the
    token request still uses the password grant;
  - `credentials.auth_type: password` — the same grant, read straight from the nested block;
  - `credentials.auth_type: oauth2.0` — a refresh_token grant against `/api/oauth2/token/`, and the
    `refresh_token_updater` emits a CONTROL message writing the fresh access token (and a rotated
    refresh token, when Uptick returns one) back into `credentials`.

All values are test fixtures; no real credentials appear anywhere.
"""

import json
from urllib.parse import parse_qs

from unit_tests.conftest import get_source

from airbyte_cdk.models import Status, SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, _run_command, make_file, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


_CHECK_STREAM = "tasks"
_TOKEN_URL = UptickRequestBuilder.token_endpoint()


def _tasks_page(record_id: int = 1) -> HttpResponse:
    record = {
        "type": "Task",
        "id": record_id,
        "attributes": {"created": "2026-01-01T00:00:00.000000+0000", "updated": "2026-01-02T00:00:00.000000+0000"},
        "relationships": {},
    }
    return HttpResponse(body=json.dumps({"data": [record], "links": {"next": None}}), status_code=200)


def _token_bodies(http_mocker: HttpMocker) -> list[dict[str, list[str]]]:
    return [parse_qs(request.body) for request in http_mocker._mocker.request_history if request.url == _TOKEN_URL]


def _control_messages(output: EntrypointOutput) -> list:
    return output.get_message_by_types([Type.CONTROL])


def test_legacy_top_level_credentials_use_password_grant(tmp_path) -> None:
    config = ConfigBuilder().build()
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(check_request, _tasks_page())

        output = _run_command(
            get_source(config=config),
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["password"]
    assert token_bodies[0]["username"] == ["test-user"]
    assert token_bodies[0]["password"] == ["test-password"]
    http_mocker.assert_number_of_calls(check_request, 1)
    # The legacy shape is normalized in memory only; the stored config is not rewritten.
    assert _control_messages(output) == []


def test_password_credentials_use_password_grant() -> None:
    config = ConfigBuilder().with_password_credentials().build()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection("servicegroups")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(page_request, _tasks_page())

        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

    assert output.errors == []
    assert output.get_stream_statuses("servicegroups")[-1].name == "COMPLETE"
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["password"]
    assert token_bodies[0]["username"] == ["test-user"]


def test_oauth_credentials_use_refresh_grant_and_emit_control() -> None:
    config = ConfigBuilder().with_oauth_credentials().build()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection("servicegroups")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "refresh_token": "rotated-refresh-token", "expires_in": 3600},
        )
        http_mocker.get(page_request, _tasks_page())

        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

    assert output.errors == []
    assert output.get_stream_statuses("servicegroups")[-1].name == "COMPLETE"
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["refresh_token"]
    assert token_bodies[0]["refresh_token"] == ["test-refresh-token"]
    assert "username" not in token_bodies[0]
    assert "password" not in token_bodies[0]
    control_messages = _control_messages(output)
    assert len(control_messages) == 1
    credentials = control_messages[0].control.connectorConfig.config["credentials"]
    assert credentials["access_token"] == "tok"
    assert credentials["refresh_token"] == "rotated-refresh-token"


def test_oauth_credentials_keep_refresh_token_when_response_omits_it() -> None:
    config = ConfigBuilder().with_oauth_credentials().build()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection("servicegroups")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(page_request, _tasks_page())

        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

    assert output.errors == []
    control_messages = _control_messages(output)
    assert len(control_messages) == 1
    credentials = control_messages[0].control.connectorConfig.config["credentials"]
    assert credentials["access_token"] == "tok"
    assert credentials["refresh_token"] == "test-refresh-token"
