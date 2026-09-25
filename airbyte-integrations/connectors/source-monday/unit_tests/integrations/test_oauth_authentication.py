# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import base64
import json
from datetime import timedelta
from unittest import TestCase
from urllib.parse import parse_qs

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse

from .config import ConfigBuilder
from .monday_requests import BoardsRequestBuilder, TeamsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import BoardsResponseBuilder, TeamsResponseBuilder
from .monday_responses.records import BoardsRecordBuilder, TeamsRecordBuilder
from .utils import _YAML_FILE_PATH, read_stream


_TOKEN_REFRESH_ENDPOINT = "https://auth.monday.com/oauth_ms/oauth/token"
_TOKEN_MIGRATION_ENDPOINT = "https://auth.monday.com/oauth_ms/oauth/migrate"


_TOKEN_RESPONSE = {"access_token": "new-access", "refresh_token": "new-refresh", "token_type": "Bearer", "scope": "boards:read"}
_MIGRATION_RESPONSE = {
    "access_token": "migrated-access",
    "refresh_token": "migrated-refresh",
    "token_type": "Bearer",
    "expires_in": 86400,
    "already_migrated": False,
    "migrated_from": {"api_token_id": 12345678},
}


def _legacy_oauth_config():
    return (
        ConfigBuilder()
        .with_oauth_credentials(client_id="client-id", client_secret="client-secret", access_token="legacy-access", subdomain="airbyte")
        .build()
    )


def _requests_to(http_mocker, url):
    return [request for request in http_mocker._mocker.request_history if request.url == url]


def _stream_error(output, stream_name):
    return next(message.trace.error for message in output.errors if message.trace.error.stream_descriptor.name == stream_name)


def _read_streams(stream_names, config, expecting_exception=False):
    catalog = CatalogBuilder()
    for stream_name in stream_names:
        catalog = catalog.with_stream(stream_name, SyncMode.full_refresh)
    catalog = catalog.build()
    source = YamlDeclarativeSource(config=config, catalog=catalog, state=None, path_to_yaml=_YAML_FILE_PATH)
    return read(source, config, catalog, None, expecting_exception)


def _jwt(payload):
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"header.{encoded}.signature"


def _migrated_token_expiry(output):
    control_messages = output.get_message_by_types([Type.CONTROL])
    assert len(control_messages) == 1
    return ab_datetime_parse(control_messages[0].control.connectorConfig.config["credentials"]["token_expiry_date"])


class TestOAuthAuthentication(TestCase):
    @HttpMocker()
    def test_given_expired_token_when_read_then_refresh_token_and_emit_control_message(self, http_mocker):
        config = (
            ConfigBuilder()
            .with_oauth_credentials(
                client_id="client-id",
                client_secret="client-secret",
                access_token="stale-access",
                subdomain="airbyte",
                refresh_token="old-refresh",
            )
            .build()
        )

        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("new-access")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )
        # Registered last so requests_mock (reverse order) matches the token URL before the teams matcher, whose
        # JSON body matcher would otherwise choke on the form-encoded refresh payload.
        http_mocker._mocker.post(_TOKEN_REFRESH_ENDPOINT, json=_TOKEN_RESPONSE)

        output = read_stream("teams", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        assert _requests_to(http_mocker, _TOKEN_MIGRATION_ENDPOINT) == []

        token_request_body = parse_qs(
            next(request.body for request in http_mocker._mocker.request_history if request.url == _TOKEN_REFRESH_ENDPOINT)
        )
        assert token_request_body["grant_type"] == ["refresh_token"]
        assert token_request_body["refresh_token"] == ["old-refresh"]
        assert token_request_body["client_id"] == ["client-id"]
        assert token_request_body["client_secret"] == ["client-secret"]

        control_messages = output.get_message_by_types([Type.CONTROL])
        assert len(control_messages) == 1
        updated_credentials = control_messages[0].control.connectorConfig.config["credentials"]
        assert updated_credentials["access_token"] == "new-access"
        assert updated_credentials["refresh_token"] == "new-refresh"
        assert updated_credentials["token_expiry_date"]

    @HttpMocker()
    def test_given_unexpired_token_when_read_then_no_token_refresh(self, http_mocker):
        config = (
            ConfigBuilder()
            .with_oauth_credentials(
                client_id="client-id",
                client_secret="client-secret",
                access_token="current-access",
                subdomain="airbyte",
                refresh_token="old-refresh",
                token_expiry_date=(ab_datetime_now() + timedelta(hours=1)).isoformat(),
            )
            .build()
        )

        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("current-access")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )

        output = read_stream("teams", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        assert [request.url for request in http_mocker._mocker.request_history if request.url == _TOKEN_REFRESH_ENDPOINT] == []
        assert output.get_message_by_types([Type.CONTROL]) == []

    @HttpMocker()
    def test_given_legacy_config_without_refresh_token_when_read_then_migrate_and_emit_control_message(self, http_mocker):
        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("migrated-access")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )
        http_mocker._mocker.post(_TOKEN_MIGRATION_ENDPOINT, json=_MIGRATION_RESPONSE)

        output = read_stream("teams", SyncMode.full_refresh, _legacy_oauth_config())

        assert len(output.records) == 1

        migration_requests = _requests_to(http_mocker, _TOKEN_MIGRATION_ENDPOINT)
        assert len(migration_requests) == 1
        assert migration_requests[0].json() == {"api_token": "legacy-access", "client_id": "client-id", "client_secret": "client-secret"}
        assert _requests_to(http_mocker, _TOKEN_REFRESH_ENDPOINT) == []

        control_messages = output.get_message_by_types([Type.CONTROL])
        assert len(control_messages) == 1
        updated_credentials = control_messages[0].control.connectorConfig.config["credentials"]
        assert updated_credentials["access_token"] == "migrated-access"
        assert updated_credentials["refresh_token"] == "migrated-refresh"
        assert ab_datetime_now() + timedelta(hours=23) < ab_datetime_parse(updated_credentials["token_expiry_date"])
        assert filter_secrets("migrated-access migrated-refresh") == "**** ****"

    @HttpMocker()
    def test_given_legacy_config_when_migration_rejected_then_config_error_asking_to_reauthenticate(self, http_mocker):
        http_mocker._mocker.post(
            _TOKEN_MIGRATION_ENDPOINT,
            status_code=401,
            json={"error": "invalid_token", "error_description": "The API token is invalid, expired, revoked, or not found"},
        )

        output = read_stream("teams", SyncMode.full_refresh, _legacy_oauth_config(), expecting_exception=True)

        assert output.records == []
        assert output.get_message_by_types([Type.CONTROL]) == []
        assert [request.url for request in http_mocker._mocker.request_history] == [_TOKEN_MIGRATION_ENDPOINT]
        error = _stream_error(output, "teams")
        assert error.failure_type == FailureType.config_error
        assert "Re-authenticate this source" in error.message
        assert "invalid, expired, revoked, or not found" in error.message

    @HttpMocker()
    def test_given_legacy_config_when_migration_rate_limited_then_transient_error(self, http_mocker):
        http_mocker._mocker.post(_TOKEN_MIGRATION_ENDPOINT, status_code=429, json={"error": "rate_limited"})

        output = read_stream("teams", SyncMode.full_refresh, _legacy_oauth_config(), expecting_exception=True)

        assert output.records == []
        assert output.get_message_by_types([Type.CONTROL]) == []
        assert _stream_error(output, "teams").failure_type == FailureType.transient_error

    @HttpMocker()
    def test_given_legacy_config_when_migration_unavailable_then_transient_error(self, http_mocker):
        http_mocker._mocker.post(_TOKEN_MIGRATION_ENDPOINT, status_code=503, text="Service Unavailable")

        output = read_stream("teams", SyncMode.full_refresh, _legacy_oauth_config(), expecting_exception=True)

        assert output.get_message_by_types([Type.CONTROL]) == []
        assert _stream_error(output, "teams").failure_type == FailureType.transient_error

    @HttpMocker()
    def test_given_legacy_config_when_reading_two_streams_then_migrate_once(self, http_mocker):
        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("migrated-access")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )
        http_mocker.post(
            BoardsRequestBuilder.boards_endpoint(ApiTokenAuthenticator("migrated-access")).build(),
            BoardsResponseBuilder.boards_response().with_record(BoardsRecordBuilder.boards_record()).build(),
        )
        http_mocker._mocker.post(_TOKEN_MIGRATION_ENDPOINT, json=_MIGRATION_RESPONSE)

        output = _read_streams(["teams", "boards"], _legacy_oauth_config())

        assert len(output.records) == 2
        assert len(_requests_to(http_mocker, _TOKEN_MIGRATION_ENDPOINT)) == 1
        assert len(output.get_message_by_types([Type.CONTROL])) == 1

    @HttpMocker()
    def test_given_legacy_config_when_migration_rejected_then_other_streams_do_not_call_migrate_again(self, http_mocker):
        http_mocker._mocker.post(_TOKEN_MIGRATION_ENDPOINT, status_code=401, json={"error": "invalid_token"})

        output = _read_streams(["teams", "boards"], _legacy_oauth_config(), expecting_exception=True)

        assert output.records == []
        assert len(_requests_to(http_mocker, _TOKEN_MIGRATION_ENDPOINT)) == 1
        assert _stream_error(output, "teams").failure_type == FailureType.config_error
        assert _stream_error(output, "boards").failure_type == FailureType.config_error

    @HttpMocker()
    def test_given_migrated_jwt_when_read_then_token_expiry_comes_from_the_exp_claim(self, http_mocker):
        exp = ab_datetime_now() + timedelta(hours=5)
        access_token = _jwt({"exp": int(exp.timestamp())})
        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator(access_token)).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )
        http_mocker._mocker.post(_TOKEN_MIGRATION_ENDPOINT, json={**_MIGRATION_RESPONSE, "access_token": access_token, "expires_in": 86400})

        output = read_stream("teams", SyncMode.full_refresh, _legacy_oauth_config())

        assert len(output.records) == 1
        assert abs((_migrated_token_expiry(output) - exp).total_seconds()) < 60

    @HttpMocker()
    def test_given_migration_response_without_expires_in_when_read_then_token_expiry_defaults_to_one_hour(self, http_mocker):
        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("migrated-access")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )
        http_mocker._mocker.post(
            _TOKEN_MIGRATION_ENDPOINT, json={key: value for key, value in _MIGRATION_RESPONSE.items() if key != "expires_in"}
        )

        output = read_stream("teams", SyncMode.full_refresh, _legacy_oauth_config())

        assert len(output.records) == 1
        assert ab_datetime_now() + timedelta(minutes=59) < _migrated_token_expiry(output) < ab_datetime_now() + timedelta(minutes=61)

    @HttpMocker()
    def test_given_api_token_config_when_read_then_no_token_refresh(self, http_mocker):
        config = ConfigBuilder().with_api_token_credentials("api-token").build()

        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("api-token")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )

        output = read_stream("teams", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        assert output.get_message_by_types([Type.CONTROL]) == []
