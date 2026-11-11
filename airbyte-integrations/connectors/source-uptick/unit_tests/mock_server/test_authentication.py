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
import socket
from contextlib import redirect_stdout
from io import StringIO
from urllib.parse import parse_qs

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, _run_command, make_file, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


_CHECK_STREAM = "tasks"
_TOKEN_URL = UptickRequestBuilder.token_endpoint()
_LEGACY_DATE_FIELDS = ("end_date", "start_date")
_LEGACY_OAUTH_TOKEN_FIELDS = ("oauth_access_token", "oauth_token_expiry_date", "client_refresh_token")
_LEGACY_CONFIG_FIELDS = _LEGACY_DATE_FIELDS + _LEGACY_OAUTH_TOKEN_FIELDS


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


def _control_messages(stdout: str) -> list[dict]:
    messages = []
    for line in stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("type") == "CONTROL":
            messages.append(message)
    return messages


def _with_control_messages(operation) -> tuple[EntrypointOutput, list[dict]]:
    stdout = StringIO()
    with redirect_stdout(stdout):
        output = operation()
    return output, _control_messages(stdout.getvalue())


def _source_with_migration_controls(config: dict):
    """Build the source, capturing the config-migration CONTROL the constructor prints to stdout.

    Like source-monday's test_config_migration.py: the migration control message is printed by the
    source constructor, so it never reaches the entrypoint output.
    """
    stdout = StringIO()
    with redirect_stdout(stdout):
        source = get_source(config=config)
    controls = [json.loads(line) for line in stdout.getvalue().splitlines() if '"CONTROL"' in line]
    return source, controls


def test_legacy_fields_are_removed_after_password_credentials_migrate() -> None:
    config = ConfigBuilder().build()
    config.update({field: "legacy-value" for field in _LEGACY_CONFIG_FIELDS})
    _, migration_controls = _source_with_migration_controls(config)

    assert migration_controls
    migrated = migration_controls[-1]["control"]["connectorConfig"]["config"]

    assert migrated["base_url"] == config["base_url"]
    assert migrated["credentials"]["auth_type"] == "password"
    assert all(field not in migrated for field in _LEGACY_CONFIG_FIELDS)


def test_legacy_oauth_tokens_are_removed_with_oauth_credentials() -> None:
    config = ConfigBuilder().with_oauth_credentials(access_token="migrated-access-token", token_expiry_date="migrated-expiry-date").build()
    config.update({field: "legacy-value" for field in _LEGACY_CONFIG_FIELDS})
    _, migration_controls = _source_with_migration_controls(config)

    assert migration_controls
    migrated = migration_controls[-1]["control"]["connectorConfig"]["config"]

    assert migrated["credentials"]["auth_type"] == "oauth2.0"
    assert all(field not in migrated for field in _LEGACY_CONFIG_FIELDS)
    assert migrated["credentials"]["access_token"] == "migrated-access-token"
    assert migrated["credentials"]["token_expiry_date"] == "migrated-expiry-date"


def test_legacy_oauth_tokens_are_kept_without_credentials() -> None:
    config = {
        "base_url": "https://test-tenant.onuptick.com",
        **{field: "legacy-value" for field in _LEGACY_CONFIG_FIELDS},
    }
    _, migration_controls = _source_with_migration_controls(config)

    assert migration_controls
    migrated = migration_controls[-1]["control"]["connectorConfig"]["config"]

    assert "credentials" not in migrated
    assert all(field not in migrated for field in _LEGACY_DATE_FIELDS)
    assert all(migrated[field] == "legacy-value" for field in _LEGACY_OAUTH_TOKEN_FIELDS)


def test_config_without_legacy_fields_emits_no_migration_control() -> None:
    config = ConfigBuilder().with_password_credentials().build()
    _, migration_controls = _source_with_migration_controls(config)

    assert migration_controls == []


@pytest.mark.parametrize(
    "credential_value, wire_value",
    [
        ("S3cret!", "S3cret!"),
        ("12345678", "12345678"),
        ("True", "True"),
        # The CDK's JinjaInterpolation literal-evals rendered values (jinja.py _literal_eval), so a
        # string that parses as a float is coerced at the authenticator use-site even though the
        # migrated config keeps the string "1e5" (value_type: string). Pins the current behaviour.
        ("1e5", "100000.0"),
    ],
)
def test_legacy_top_level_credentials_use_password_grant(credential_value: str, wire_value: str, tmp_path) -> None:
    config = ConfigBuilder().build()
    config["password"] = credential_value
    config["client_id"] = credential_value
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)
    source, migration_controls = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(check_request, _tasks_page())

        output, control_messages = _with_control_messages(
            lambda: _run_command(
                source,
                ["check", "--config", make_file(tmp_path / "config.json", config)],
            )
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["password"]
    assert token_bodies[0]["username"] == ["test-user"]
    assert token_bodies[0]["password"] == [wire_value]
    assert token_bodies[0]["client_id"] == [wire_value]
    http_mocker.assert_number_of_calls(check_request, 1)
    # The legacy shape is migrated once: exactly one CONTROL copies the credentials under
    # `credentials` while keeping the top-level fields (rollback-safe for <=2.0.x).
    assert control_messages == []
    assert len(migration_controls) == 1
    migrated = migration_controls[0]["control"]["connectorConfig"]["config"]
    credentials = migrated["credentials"]
    assert credentials["auth_type"] == "password"
    assert credentials["client_id"] == credential_value
    assert credentials["client_secret"] == "test-client-secret"
    assert credentials["username"] == "test-user"
    assert credentials["password"] == credential_value
    for field in ("client_id", "client_secret", "username", "password"):
        assert isinstance(credentials[field], str)
        assert migrated[field] == credentials[field]
    assert migrated["base_url"] == "https://test-tenant.onuptick.com"


def test_password_credentials_use_password_grant() -> None:
    config = ConfigBuilder().with_password_credentials().build()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection("servicegroups")
    source, migration_controls = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(page_request, _tasks_page())

        output, control_messages = _with_control_messages(
            lambda: read(source, config=config, catalog=catalog, state=StateBuilder().build())
        )

    assert output.errors == []
    assert output.get_stream_statuses("servicegroups")[-1].name == "COMPLETE"
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["password"]
    assert token_bodies[0]["username"] == ["test-user"]
    # No migration fires for this shape, so 0 CONTROL.
    assert source._config["base_url"] == "https://test-tenant.onuptick.com"
    assert migration_controls == []
    assert control_messages == []


def test_password_credentials_without_any_base_url_fails_check(tmp_path) -> None:
    config = ConfigBuilder().with_password_credentials().build()
    del config["base_url"]
    source, migration_controls = _source_with_migration_controls(config)

    assert migration_controls == []
    assert "base_url" not in source._config

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )

        output = _run_command(
            source,
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.FAILED
    # Top-level `base_url` is required, so entrypoint spec validation fails the check before any
    # token request.
    assert statuses[0].connectionStatus.message == "Config validation error: 'base_url' is a required property"
    assert _token_bodies(http_mocker) == []


def test_oauth_credentials_use_refresh_grant_and_emit_control() -> None:
    config = ConfigBuilder().with_oauth_credentials().build()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection("servicegroups")
    source, migration_controls = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "refresh_token": "rotated-refresh-token", "expires_in": 3600},
        )
        http_mocker.get(page_request, _tasks_page())

        output, control_messages = _with_control_messages(
            lambda: read(source, config=config, catalog=catalog, state=StateBuilder().build())
        )

    assert output.errors == []
    assert output.get_stream_statuses("servicegroups")[-1].name == "COMPLETE"
    assert migration_controls == []
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    # The OAuth token refresh endpoint is the host pinned by config_normalization_rules.
    assert [request.url for request in http_mocker._mocker.request_history if request.url == _TOKEN_URL] == [
        "https://test-tenant.onuptick.com/api/oauth2/token/"
    ]
    assert token_bodies[0]["grant_type"] == ["refresh_token"]
    assert token_bodies[0]["refresh_token"] == ["test-refresh-token"]
    assert "username" not in token_bodies[0]
    assert "password" not in token_bodies[0]
    # Exactly one CONTROL: the refresh_token_updater writing back rotated credentials.
    assert len(control_messages) == 1
    persisted_config = control_messages[0]["control"]["connectorConfig"]["config"]
    credentials = persisted_config["credentials"]
    assert credentials["access_token"] == "tok"
    assert credentials["refresh_token"] == "rotated-refresh-token"


def test_oauth_trailing_slash_base_url_uses_normalized_host(tmp_path) -> None:
    config = ConfigBuilder().with_base_url("https://test-tenant.onuptick.com/").with_oauth_credentials().build()
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)
    source, _ = _source_with_migration_controls(config)
    assert source._config["base_url"] == "https://test-tenant.onuptick.com"

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(check_request, _tasks_page())

        output = _run_command(
            source,
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert [request.url for request in http_mocker._mocker.request_history if request.url.endswith("/api/oauth2/token/")] == [_TOKEN_URL]
    assert token_bodies[0]["grant_type"] == ["refresh_token"]
    http_mocker.assert_number_of_calls(check_request, 1)


def _check_with_network_blocked(source, config, tmp_path, monkeypatch) -> tuple[EntrypointOutput, list]:
    # No requests_mock here: it intercepts adapter resolution, which would change the prod
    # failure path. Block the real socket layer instead so any outbound attempt fails loudly.
    socket_calls: list = []

    def _blocked_socket(*args, **kwargs):
        socket_calls.append((args, kwargs))
        raise RuntimeError("socket creation blocked by test")

    def _blocked_getaddrinfo(*args, **kwargs):
        socket_calls.append(("getaddrinfo", args))
        raise RuntimeError("getaddrinfo blocked by test")

    monkeypatch.setattr(socket, "socket", _blocked_socket)
    monkeypatch.setattr(socket, "getaddrinfo", _blocked_getaddrinfo)

    output = _run_command(
        source,
        ["check", "--config", make_file(tmp_path / "config.json", config)],
    )
    return output, socket_calls


# Both shapes the platform can hand the connector: a cold config (refresh first) and the persisted
# shape after consent or a refresh CONTROL (a still-valid access_token, so no refresh by default).
_OAUTH_TOKEN_SHAPES = pytest.mark.parametrize(
    "stored_token",
    [
        pytest.param({}, id="no_stored_token"),
        pytest.param({"access_token": "LIVE-ACCESS-TOKEN", "token_expiry_date": "2099-01-01T00:00:00Z"}, id="valid_stored_token"),
    ],
)


@_OAUTH_TOKEN_SHAPES
def test_oauth_non_onuptick_base_url_fails_check_without_requests(stored_token, tmp_path, monkeypatch) -> None:
    # A post-creation edit of base_url to another host is rejected before the authenticator
    # can send credentials or a still-valid stored access token.
    config = ConfigBuilder().with_base_url("https://evil.example.com").with_oauth_credentials(**stored_token).build()
    source, _ = _source_with_migration_controls(config)

    output, socket_calls = _check_with_network_blocked(source, config, tmp_path, monkeypatch)

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.FAILED
    assert "does not match" in statuses[0].connectionStatus.message
    assert "onuptick" in statuses[0].connectionStatus.message
    assert socket_calls == []


@_OAUTH_TOKEN_SHAPES
def test_oauth_uppercase_host_base_url_fails_check_without_requests(stored_token, tmp_path, monkeypatch) -> None:
    # The host match is case-sensitive, consistent with the advanced_auth pattern.
    config = ConfigBuilder().with_base_url("https://Test-Tenant.onuptick.com").with_oauth_credentials(**stored_token).build()
    source, _ = _source_with_migration_controls(config)

    output, socket_calls = _check_with_network_blocked(source, config, tmp_path, monkeypatch)

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.FAILED
    assert "base_url-must-be-https-workspace.onuptick.com" in statuses[0].connectionStatus.message
    assert socket_calls == []


@pytest.mark.parametrize(
    "base_url, expect_pattern_message",
    [
        pytest.param("https://www.uptickhq.com", True, id="uptick-homepage"),
        pytest.param("https://example.com", True, id="example-domain"),
        pytest.param("http://localhost:8000", True, id="self-hosted"),
        pytest.param("", False, id="empty"),
    ],
)
def test_password_non_uptick_base_url_fails_check_without_token_request(base_url: str, expect_pattern_message: bool, tmp_path) -> None:
    config = ConfigBuilder().with_base_url(base_url).with_password_credentials().build()
    source, _ = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        output = _run_command(
            source,
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.FAILED
    if expect_pattern_message:
        assert "does not match" in statuses[0].connectionStatus.message
        assert "onuptick" in statuses[0].connectionStatus.message
    assert http_mocker._mocker.request_history == []


@pytest.mark.parametrize(
    "base_url, expected_base_url, expected_request_base_url",
    [
        pytest.param(
            "https://test-tenant.onuptick.com",
            "https://test-tenant.onuptick.com",
            "https://test-tenant.onuptick.com",
            id="normal",
        ),
        pytest.param("HTTPS://Tenant.ONUPTICK.com", "https://Tenant.ONUPTICK.com", "https://tenant.onuptick.com", id="uppercase"),
        pytest.param(
            "https://test-tenant.onuptick.com/app/",
            "https://test-tenant.onuptick.com",
            "https://test-tenant.onuptick.com",
            id="path-suffix",
        ),
    ],
)
def test_password_valid_base_urls_reach_normalized_token_host(
    base_url: str, expected_base_url: str, expected_request_base_url: str, tmp_path
) -> None:
    config = ConfigBuilder().with_base_url(base_url).with_password_credentials().build()
    source, _ = _source_with_migration_controls(config)
    assert source._config["base_url"] == expected_base_url
    token_url = UptickRequestBuilder.token_endpoint(base_url=expected_request_base_url)
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM, base_url=expected_request_base_url)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(token_url, json={"access_token": "tok", "expires_in": 3600})
        http_mocker.get(check_request, _tasks_page())
        output = _run_command(
            source,
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_requests = [request for request in http_mocker._mocker.request_history if request.url.endswith("/api/oauth2/token/")]
    assert [request.url for request in token_requests] == [token_url]
    http_mocker.assert_number_of_calls(check_request, 1)


def test_stale_base_url_json_is_overwritten_before_check(tmp_path) -> None:
    config = ConfigBuilder().with_base_url("https://test-tenant.onuptick.com").with_password_credentials().build()
    config["base_url_json"] = '"https://evil.example.com"'
    config_path = make_file(tmp_path / "config.json", config)
    source, _ = _source_with_migration_controls(config)
    assert source._config["base_url_json"] == '"https://test-tenant.onuptick.com"'
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, json={"access_token": "tok", "expires_in": 3600})
        http_mocker.get(check_request, _tasks_page())
        output = _run_command(source, ["check", "--config", config_path])

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_requests = [request for request in http_mocker._mocker.request_history if request.url.endswith("/api/oauth2/token/")]
    assert [request.url for request in token_requests] == [_TOKEN_URL]
    http_mocker.assert_number_of_calls(check_request, 1)


def test_base_url_only_config_fails_check(tmp_path) -> None:
    config = {"base_url": "https://test-tenant.onuptick.com"}

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )

        output = _run_command(
            get_source(config=config),
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.FAILED
    # With no `credentials` key the authenticator fails before any token request is made.
    assert _token_bodies(http_mocker) == []


def test_config_with_both_credential_shapes_copies_nothing(tmp_path) -> None:
    # Already-migrated config (top-level fields kept alongside nested credentials): no migration
    # copy re-fires and the password grant still works.
    config = ConfigBuilder().with_password_credentials().build()
    config["client_id"] = "test-client-id"
    config["client_secret"] = "test-client-secret"
    config["username"] = "test-user"
    config["password"] = "test-password"
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)
    source, migration_controls = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(check_request, _tasks_page())

        output, control_messages = _with_control_messages(
            lambda: _run_command(
                source,
                ["check", "--config", make_file(tmp_path / "config.json", config)],
            )
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["password"]
    assert migration_controls == []
    assert control_messages == []


def test_empty_config_fails_check_without_token_request(tmp_path) -> None:
    config: dict = {}
    source, _ = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )

        output = _run_command(
            source,
            ["check", "--config", make_file(tmp_path / "config.json", config)],
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.FAILED
    assert _token_bodies(http_mocker) == []


def test_legacy_top_level_credentials_with_empty_credentials_object(tmp_path) -> None:
    config = {**ConfigBuilder().build(), "credentials": {}}
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)
    source, migration_controls = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(check_request, _tasks_page())

        output, control_messages = _with_control_messages(
            lambda: _run_command(
                source,
                ["check", "--config", make_file(tmp_path / "config.json", config)],
            )
        )

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    token_bodies = _token_bodies(http_mocker)
    assert len(token_bodies) == 1
    assert token_bodies[0]["grant_type"] == ["password"]
    # The empty `credentials` object is filled in place by the migration (auth_type=password).
    assert source._config["credentials"]["auth_type"] == "password"
    # No CONTROL: the CDK's migrate-and-diff compares a shallow `dict(config)` copy, and the nested
    # object mutated in place is shared with the original, so the change is invisible to the diff.
    assert migration_controls == []
    assert control_messages == []


def test_oauth_credentials_keep_refresh_token_when_response_omits_it() -> None:
    config = ConfigBuilder().with_oauth_credentials().build()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection("servicegroups")
    source, migration_controls = _source_with_migration_controls(config)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "tok", "expires_in": 3600},
        )
        http_mocker.get(page_request, _tasks_page())

        output, control_messages = _with_control_messages(
            lambda: read(source, config=config, catalog=catalog, state=StateBuilder().build())
        )

    assert output.errors == []
    assert migration_controls == []
    assert len(control_messages) == 1
    credentials = control_messages[0]["control"]["connectorConfig"]["config"]["credentials"]
    assert credentials["access_token"] == "tok"
    assert credentials["refresh_token"] == "test-refresh-token"
