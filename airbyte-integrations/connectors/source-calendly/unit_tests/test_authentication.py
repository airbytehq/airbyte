# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
import logging
from typing import Any, Mapping

import pytest
from _helpers import CONFIG, USER, collection, list_request, mock_user, read_stream, request
from conftest import get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


TOKEN_URL = "https://auth.calendly.com/oauth/token"
BASIC_AUTH = "Basic " + base64.b64encode(b"test_client_id:test_client_secret").decode()


def oauth_config(**credentials: str) -> dict[str, Any]:
    # The authenticator writes refreshed tokens into the config it is given, so each test needs a fresh one.
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "old_refresh_token",
            **credentials,
        },
        "start_date": "2024-01-01T00:00:00Z",
    }


def token_request() -> HttpRequest:
    return HttpRequest(
        url=TOKEN_URL,
        headers={"Authorization": BASIC_AUTH},
        body="grant_type=refresh_token&refresh_token=old_refresh_token&client_id=test_client_id",
    )


def token_response() -> HttpResponse:
    body = {
        "token_type": "Bearer",
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 7200,
        "created_at": 1704067200,
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


def emitted_configs(capsys: pytest.CaptureFixture[str]) -> list[Mapping[str, Any]]:
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    return [message["control"]["connectorConfig"]["config"] for message in messages if message.get("type") == "CONTROL"]


def read_streams(stream_names: list[str], config: Mapping[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder()
    for name in stream_names:
        catalog = catalog.with_stream(name, SyncMode.full_refresh)
    return read(get_source(config), config, catalog.build())


@pytest.mark.parametrize(
    "legacy_config",
    [
        # A digit-only token would become an integer without `value_type: string`.
        {"api_key": "1234567890", "start_date": "2024-01-01T00:00:00Z"},
        # A stale top-level key next to migrated credentials is dropped, not copied.
        {"api_key": "1234567890", "credentials": {"auth_type": "api_key", "api_key": "1234567890"}, "start_date": "2024-01-01T00:00:00Z"},
    ],
)
def test_legacy_top_level_token_is_moved_into_credentials(legacy_config: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    with HttpMocker() as http:
        target = mock_user(http, token="1234567890")
        output = read_stream("api_user", legacy_config)
        assert not output.errors
        assert [record.record.data for record in output.records] == [USER]
        # The platform saves this config, so the token must not stay at the top level where the spec no longer masks it.
        assert emitted_configs(capsys)[0] == {
            "credentials": {"auth_type": "api_key", "api_key": "1234567890"},
            "start_date": "2024-01-01T00:00:00Z",
        }
        http.assert_number_of_calls(target, 1)


def test_personal_access_token_in_credentials_authenticates_requests(capsys: pytest.CaptureFixture[str]) -> None:
    config = {"credentials": {"auth_type": "api_key", "api_key": "nested_api_key"}, "start_date": "2024-01-01T00:00:00Z"}
    with HttpMocker() as http:
        target = mock_user(http, token="nested_api_key")
        output = read_stream("api_user", config)
        assert not output.errors
        assert [record.record.data for record in output.records] == [USER]
        assert not emitted_configs(capsys)
        http.assert_number_of_calls(target, 1)


def test_oauth_refresh_rotates_and_persists_tokens(capsys: pytest.CaptureFixture[str]) -> None:
    with HttpMocker() as http:
        http.post(token_request(), token_response())
        user = mock_user(http, token="new_access_token")
        output = read_stream("api_user", oauth_config())
        assert not output.errors
        assert [record.record.data for record in output.records] == [USER]
        credentials = emitted_configs(capsys)[-1]["credentials"]
        assert credentials["access_token"] == "new_access_token"
        assert credentials["refresh_token"] == "new_refresh_token"
        assert credentials["token_expiry_date"]
        http.assert_number_of_calls(user, 1)


def test_oauth_requests_one_token_for_all_streams() -> None:
    with HttpMocker() as http:
        token = token_request()
        http.post(token, token_response())
        mock_user(http, token="new_access_token")
        http.get(list_request("event_types", token="new_access_token"), collection([{"uri": "https://api.calendly.com/event_types/1"}]))
        http.get(list_request("groups", token="new_access_token"), collection([{"uri": "https://api.calendly.com/groups/1"}]))
        output = read_streams(["api_user", "event_types", "groups"], oauth_config())
        assert not output.errors
        assert {record.record.stream for record in output.records} == {"api_user", "event_types", "groups"}
        http.assert_number_of_calls(token, 1)


def test_oauth_reuses_unexpired_stored_access_token() -> None:
    config = oauth_config(access_token="stored_access_token", token_expiry_date="2099-01-01T00:00:00Z")
    with HttpMocker() as http:
        target = mock_user(http, token="stored_access_token")
        output = read_stream("api_user", config)
        assert not output.errors
        assert [record.record.data for record in output.records] == [USER]
        http.assert_number_of_calls(target, 1)


def test_oauth_invalid_grant_asks_to_reauthenticate() -> None:
    with HttpMocker() as http:
        body = {"error": "invalid_grant", "error_description": "The provided authorization grant is invalid"}
        http.post(token_request(), HttpResponse(body=json.dumps(body), status_code=400))
        output = read_stream("api_user", oauth_config())
        assert not output.records
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "Calendly rejected the OAuth refresh token" in error.message
        assert "Re-authenticate with Calendly in the Airbyte source settings" in error.message


def test_oauth_check_with_revoked_access_token_asks_to_reauthenticate() -> None:
    config = oauth_config(access_token="revoked_access_token", token_expiry_date="2099-01-01T00:00:00Z")
    with HttpMocker() as http:
        target = request("users/me", token="revoked_access_token")
        http.get(target, HttpResponse(body='{"title":"Unauthenticated","message":"Token revoked"}', status_code=401))
        status = get_source(config).check(logging.getLogger("airbyte"), config)
        assert status.status == Status.FAILED
        assert "If the source uses OAuth, re-authenticate with Calendly in the Airbyte source settings" in status.message
        assert "Calendly response (401): Token revoked" in status.message
        http.assert_number_of_calls(target, 1)
