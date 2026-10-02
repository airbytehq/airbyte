# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import yaml

from airbyte_cdk.models import FailureType, SyncMode, Type
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

USERS_RESPONSE = {
    "data": [
        {
            "type": "user",
            "id": 1,
            "attributes": {"name": "Test User", "updatedAt": "2026-09-01T00:00:00.000Z"},
            "relationships": {},
        }
    ],
    "links": {},
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


def _read_users(get_source, expecting_exception=False):
    catalog = CatalogBuilder().with_stream("users", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), config=CONFIG, catalog=catalog, expecting_exception=expecting_exception)


def test_rotated_tokens_are_saved_to_config(requests_mock, get_source):
    _register_token_endpoint(requests_mock)
    requests_mock.get(USERS_URL, json=USERS_RESPONSE)

    output = _read_users(get_source)

    control_messages = output.get_message_by_types([Type.CONTROL])
    assert control_messages, "expected a CONNECTOR_CONFIG control message that saves the rotated tokens"
    saved_config = control_messages[-1].control.connectorConfig.config
    assert saved_config["refresh_token"] == "refresh-token-1"
    assert saved_config["access_token"] == "token-1"
    assert saved_config["token_expiry_date"]
    assert [record.record.data["id"] for record in output.records] == [1]


def test_401_refreshes_token_once_then_retries(requests_mock, get_source):
    token_requests = _register_token_endpoint(requests_mock)
    users_requests = []

    def users_callback(request, context):
        users_requests.append(request)
        if request.headers["Authorization"] == "Bearer token-1":
            context.status_code = 401
            return {"errors": [{"title": "Unauthorized"}]}
        context.status_code = 200
        return USERS_RESPONSE

    requests_mock.get(USERS_URL, json=users_callback)

    output = _read_users(get_source)

    assert len(token_requests) == 2
    assert len(users_requests) == 2
    assert users_requests[1].headers["Authorization"] == "Bearer token-2"
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]


def test_401_after_refresh_fails_without_refreshing_again(requests_mock, get_source):
    token_requests = _register_token_endpoint(requests_mock)
    requests_mock.get(USERS_URL, status_code=401, json={"errors": [{"title": "Unauthorized"}]})

    output = _read_users(get_source, expecting_exception=True)

    # One token request at the start and one refresh after the first 401. No refresh loop.
    assert len(token_requests) == 2
    assert output.errors
    assert any("rejected" in trace.trace.error.message for trace in output.errors)
    assert all(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)


@pytest.mark.parametrize(
    "status_code, error",
    [
        pytest.param(400, "invalid_grant", id="refresh_token_expired_or_replaced"),
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


def test_every_stream_uses_the_shared_requester(connector_path):
    manifest = yaml.safe_load((connector_path / "manifest.yaml").read_text())

    streams = manifest["definitions"]["streams"]
    assert len(streams) == 17
    for name, stream in streams.items():
        requester = stream["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/base_requester", name
        assert "authenticator" not in requester, name
        assert "error_handler" not in requester, name
