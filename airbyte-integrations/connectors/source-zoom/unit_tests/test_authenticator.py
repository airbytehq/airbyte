# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the Zoom Server-to-Server OAuth `account_credentials` token flow.

Zoom issues access tokens from `POST {authorization_endpoint}?grant_type=account_credentials&account_id=...`
with the client credentials in an `Authorization: Basic ...` header, and answers invalid credentials
with an OAuth `error` such as `invalid_client` (bad client ID/secret, or a disabled app), `invalid_request`
(bad account ID) or `unsupported_grant_type` (credentials of a non Server-to-Server app). See
https://developers.zoom.us/docs/internal-apps/s2s-oauth/ and
https://developers.zoom.us/blog/s2s-token-generation-troubleshoot/

Zoom rejects an access token with HTTP 401 and code 124 from the moment it expires, so a request racing
the hourly expiry must refresh the token and retry instead of failing the sync.
"""

import base64
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CI_MANIFEST_DIR = Path("/airbyte/integration_code/source_declarative_manifest")
_MANIFEST_DIR = _CI_MANIFEST_DIR if _CI_MANIFEST_DIR.exists() else Path(__file__).parent.parent
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.yaml"

_TOKEN_URL = "https://zoom.us/oauth/token"
_USERS_URL = "https://api.zoom.us/v2/users"
_ZOOM_ERROR_HANDLER_REF = "#/definitions/zoom_error_handler"
_CONFIG = {
    "account_id": "test_account_id",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "authorization_endpoint": _TOKEN_URL,
}


def _read(stream_name: str = "users", expecting_exception: bool = False):
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog, expecting_exception=expecting_exception)


def _check():
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    return source.check(logger=source.logger, config=_CONFIG)


def test_manifest_has_no_custom_components():
    manifest_text = _MANIFEST_PATH.read_text()
    assert "class_name" not in manifest_text
    assert "CustomAuthenticator" not in manifest_text
    assert not (_MANIFEST_DIR / "components.py").exists()
    manifest = yaml.safe_load(manifest_text)
    assert manifest["definitions"]["authenticator"]["type"] == "OAuthAuthenticator"


def test_token_is_requested_with_account_credentials_grant_and_used_as_bearer():
    expected_basic = base64.b64encode(b"test_client_id:test_client_secret").decode()
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(_TOKEN_URL, json={"access_token": "test_access_token", "token_type": "bearer", "expires_in": 3599})
        users_mock = mocker.get(_USERS_URL, json={"users": [{"id": "u1", "email": "a@example.com"}], "next_page_token": ""})

        output = _read()

    assert [record.record.data["id"] for record in output.records] == ["u1"]

    assert token_mock.call_count == 1
    token_request = token_mock.request_history[0]
    assert parse_qs(urlparse(token_request.url).query, keep_blank_values=True) == {
        "grant_type": ["account_credentials"],
        "account_id": ["test_account_id"],
    }
    assert token_request.headers["Authorization"] == f"Basic {expected_basic}"
    assert not token_request.body

    assert users_mock.call_count == 1
    assert users_mock.request_history[0].headers["Authorization"] == "Bearer test_access_token"


@pytest.mark.parametrize(
    "status_code, error_body",
    [
        pytest.param(400, {"reason": "Invalid client_id or client_secret", "error": "invalid_client"}, id="invalid_client"),
        pytest.param(401, {"reason": "Invalid client_id or client_secret", "error": "invalid_client"}, id="invalid_client_401"),
        pytest.param(404, {"reason": "The application is disabled", "error": "invalid_client"}, id="disabled_app"),
        pytest.param(400, {"reason": "Bad Request", "error": "invalid_request"}, id="invalid_account_id"),
        pytest.param(400, {"reason": "unsupported grant type", "error": "unsupported_grant_type"}, id="not_a_s2s_app"),
    ],
)
def test_invalid_credentials_raise_config_error(status_code, error_body):
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, status_code=status_code, json=error_body)
        users_mock = mocker.get(_USERS_URL, json={"users": [], "next_page_token": ""})

        output = _read(expecting_exception=True)

    assert users_mock.call_count == 0
    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert error_body["error"] in output.errors[0].trace.error.message


def test_check_fails_on_invalid_credentials():
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, status_code=400, json={"reason": "Invalid client_id or client_secret", "error": "invalid_client"})

        status = _check()

    assert status.status == Status.FAILED
    assert "invalid_client" in status.message


def _requesters(node):
    if isinstance(node, dict):
        if isinstance(node.get("requester"), dict):
            yield node["requester"]
        for value in node.values():
            yield from _requesters(value)
    elif isinstance(node, list):
        for value in node:
            yield from _requesters(value)


def test_every_requester_uses_the_shared_authenticator_and_token_refresh_handler():
    """The manifest inlines every requester, so a copy that misses the shared blocks would ship silently.

    In a CompositeErrorHandler only SUCCESS/RETRY/IGNORE stop early, so the 124 handler must be the last child,
    otherwise the default 401 >> FAIL of a later child overrides REFRESH_TOKEN_THEN_RETRY.
    """
    requesters = list(_requesters(yaml.safe_load(_MANIFEST_PATH.read_text())))
    assert requesters
    for requester in requesters:
        assert requester.get("authenticator") == "#/definitions/authenticator"
        error_handler = requester.get("error_handler")
        if isinstance(error_handler, dict):
            assert error_handler["type"] == "CompositeErrorHandler"
            assert error_handler["error_handlers"][-1] == _ZOOM_ERROR_HANDLER_REF
        else:
            assert error_handler == _ZOOM_ERROR_HANDLER_REF


def _token_responses():
    return [{"json": {"access_token": f"test_access_token_{i}", "token_type": "bearer", "expires_in": 3599}} for i in range(1, 9)]


@patch("time.sleep")
def test_token_expired_mid_sync_is_refreshed_and_request_retried(_sleep):
    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(_TOKEN_URL, _token_responses())
        mocker.get(
            _USERS_URL,
            [
                {"json": {"users": [{"id": "u1"}], "next_page_token": "p2"}},
                {"status_code": 401, "json": {"code": 124, "message": "Invalid access token."}},
                {"json": {"users": [{"id": "u2"}], "next_page_token": ""}},
            ],
        )

        output = _read()

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["u1", "u2"]
    assert token_mock.call_count == 2


@patch("time.sleep")
def test_token_expired_mid_sync_is_refreshed_behind_a_composite_error_handler(_sleep):
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, _token_responses())
        mocker.get(_USERS_URL, json={"users": [{"id": "u1"}], "next_page_token": ""})
        user_meetings_mock = mocker.get(
            f"{_USERS_URL}/u1/meetings",
            [
                {"status_code": 401, "json": {"code": 124, "message": "Access token is expired."}},
                {"json": {"meetings": [{"id": 1}], "next_page_token": ""}},
            ],
        )
        mocker.get("https://api.zoom.us/v2/meetings/1", json={"id": 1, "topic": "t"})

        output = _read("meetings")

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == [1]
    assert user_meetings_mock.call_count == 2
