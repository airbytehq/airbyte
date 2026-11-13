# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

import pytest
import yaml

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


TOKEN_URL = "https://api.outreach.io/oauth/token"
USERS_URL = "https://api.outreach.io/api/v2/users"

CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2026-01-01T00:00:00Z",
}

UNAUTHORIZED = {"errors": [{"title": "Unauthorized"}]}


def _users_page(user_id, next_cursor=None):
    return {
        "data": [
            {
                "type": "user",
                "id": user_id,
                "attributes": {"name": "Test User", "updatedAt": "2026-09-01T00:00:00.000Z"},
                "relationships": {},
            }
        ],
        "links": {"next": f"{USERS_URL}?page[after]={next_cursor}"} if next_cursor else {},
    }


def _token_response(number):
    # Same fields as the token response in https://developers.outreach.io/api/getting-started
    return {
        "access_token": f"token-{number}",
        "token_type": "bearer",
        "expires_in": 7200,
        "refresh_token": f"refresh-token-{number}",
        "scope": "users.read",
        "created_at": 1790000000,
    }


def _register_token_endpoint(requests_mock):
    token_requests = []

    def token_callback(request, context):
        token_requests.append(request)
        context.status_code = 200
        return _token_response(len(token_requests))

    requests_mock.post(TOKEN_URL, json=token_callback)
    return token_requests


def _refresh_request_body(refresh_token):
    return {
        "grant_type": ["refresh_token"],
        "client_id": ["test-client-id"],
        "client_secret": ["test-client-secret"],
        "refresh_token": [refresh_token],
    }


def _read_users(get_source, config=CONFIG, expecting_exception=False):
    catalog = CatalogBuilder().with_stream("users", SyncMode.full_refresh).build()
    return read(get_source(config), config=config, catalog=catalog, expecting_exception=expecting_exception)


def _saved_configs(capsys):
    # Since airbyte-cdk 7.37.1 the rotated-token CONNECTOR_CONFIG message is printed to stdout
    # instead of going through the read() output (airbyte-python-cdk#1145), so read it from there.
    saved_configs = []
    for line in capsys.readouterr().out.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(message, dict) or message.get("type") != "CONTROL":
            continue

        control = message.get("control")
        if isinstance(control, dict) and control.get("type") == "CONNECTOR_CONFIG":
            saved_configs.append(control["connectorConfig"]["config"])

    return saved_configs


def test_rotated_tokens_are_saved_to_config(requests_mock, get_source, capsys):
    token_requests = _register_token_endpoint(requests_mock)
    requests_mock.get(USERS_URL, json=_users_page(1))

    output = _read_users(get_source)

    assert [parse_qs(request.text) for request in token_requests] == [_refresh_request_body("test-refresh-token")]
    saved_configs = _saved_configs(capsys)
    assert saved_configs, "expected a CONNECTOR_CONFIG control message that saves the rotated tokens"
    assert saved_configs[-1]["refresh_token"] == "refresh-token-1"
    assert saved_configs[-1]["access_token"] == "token-1"
    expiry = datetime.fromisoformat(saved_configs[-1]["token_expiry_date"])
    assert expiry.utcoffset() == timedelta(0)
    assert abs(expiry - (datetime.now(timezone.utc) + timedelta(seconds=7200))) < timedelta(minutes=1)
    assert [record.record.data["id"] for record in output.records] == [1]


def test_401_mid_sync_refreshes_with_the_latest_refresh_token(requests_mock, get_source, capsys):
    token_requests = _register_token_endpoint(requests_mock)
    sent_auth_headers = []

    def users_callback(request, context):
        # Record the header now: the CDK retries the same request object and rewrites its headers.
        sent_auth_headers.append(request.headers["Authorization"])
        cursor = request.qs.get("page[after]", [None])[0]
        if cursor is None:
            return _users_page(1, next_cursor="2")
        if cursor == "2" and request.headers["Authorization"] == "Bearer token-1":
            context.status_code = 401
            return UNAUTHORIZED
        if cursor == "2":
            return _users_page(2, next_cursor="3")
        return _users_page(3)

    requests_mock.get(USERS_URL, json=users_callback)

    output = _read_users(get_source)

    # The refresh after the 401 sends the refresh token Outreach returned last, not the original one.
    assert [parse_qs(request.text) for request in token_requests] == [
        _refresh_request_body("test-refresh-token"),
        _refresh_request_body("refresh-token-1"),
    ]
    assert sent_auth_headers == ["Bearer token-1", "Bearer token-1", "Bearer token-2", "Bearer token-2"]
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1, 2, 3]
    saved_config = _saved_configs(capsys)[-1]
    assert (saved_config["refresh_token"], saved_config["access_token"]) == ("refresh-token-2", "token-2")


def test_401_after_refresh_fails_without_refreshing_again(requests_mock, get_source):
    token_requests = _register_token_endpoint(requests_mock)
    sent_auth_headers = []

    def users_callback(request, context):
        sent_auth_headers.append(request.headers["Authorization"])
        context.status_code = 401
        return UNAUTHORIZED

    requests_mock.get(USERS_URL, json=users_callback)

    output = _read_users(get_source, expecting_exception=True)

    # One token request at the start and one refresh after the first 401. No refresh loop.
    assert len(token_requests) == 2
    assert sent_auth_headers == ["Bearer token-1", "Bearer token-2"]
    messages = [trace.trace.error.message for trace in output.errors]
    assert "Refreshed OAuth access token is rejected by the API." in messages, messages
    assert all(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)


@pytest.mark.parametrize(
    "status_code, error",
    [
        # The CDK's defaults when a manifest sets no refresh_token_error values. The manifest keeps them.
        pytest.param(400, "invalid_grant", id="refresh_token_expired_or_replaced"),
        pytest.param(400, "invalid_permissions", id="cdk_default_value_kept"),
        # Added by the manifest.
        pytest.param(401, "invalid_client", id="bad_client_credentials"),
        pytest.param(400, "unauthorized_client", id="client_not_allowed_grant"),
    ],
)
def test_refresh_rejection_asks_to_reauthenticate(status_code, error, requests_mock, get_source):
    # Outreach's docs don't show an error body, so this uses the OAuth 2.0 error format (RFC 6749, section 5.2).
    requests_mock.post(
        TOKEN_URL,
        status_code=status_code,
        json={"error": error, "error_description": "The refresh token is no longer valid."},
    )

    output = _read_users(get_source, expecting_exception=True)

    messages = [trace.trace.error.message for trace in output.errors]
    assert any("e-authenticate" in message for message in messages), messages
    assert all(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)


def test_next_sync_reuses_the_saved_access_token(requests_mock, get_source, capsys):
    token_requests = _register_token_endpoint(requests_mock)
    requests_mock.get(USERS_URL, json=_users_page(1))
    _read_users(get_source)
    saved_config = _saved_configs(capsys)[-1]
    sent_auth_headers = []

    def users_callback(request, context):
        sent_auth_headers.append(request.headers["Authorization"])
        return _users_page(1)

    requests_mock.get(USERS_URL, json=users_callback)

    output = _read_users(get_source, config=saved_config)

    assert len(token_requests) == 1, "the second sync should not ask for a new token"
    assert sent_auth_headers == ["Bearer token-1"]
    assert not output.errors
    assert not _saved_configs(capsys), "the second sync should not save a new config"


def test_every_stream_uses_the_shared_requester(connector_path):
    manifest = yaml.safe_load((connector_path / "manifest.yaml").read_text())

    streams = manifest["definitions"]["streams"]
    assert streams
    assert all(set(entry) == {"$ref"} for entry in manifest["streams"])
    assert {entry["$ref"] for entry in manifest["streams"]} == {f"#/definitions/streams/{name}" for name in streams}
    for name, stream in streams.items():
        requester = stream["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/base_requester", name
        assert "authenticator" not in requester, name
        assert "error_handler" not in requester, name
