# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the Zoom Server-to-Server OAuth `account_credentials` token flow.

Zoom issues access tokens from `POST {authorization_endpoint}?grant_type=account_credentials&account_id=...`
with the client credentials in an `Authorization: Basic ...` header, and answers invalid credentials
with HTTP 400 and an OAuth `error` of `invalid_client` (bad client ID/secret) or `invalid_request`
(bad account ID). See https://developers.zoom.us/docs/internal-apps/s2s-oauth/
"""

import base64
from pathlib import Path
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
_CONFIG = {
    "account_id": "test_account_id",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "authorization_endpoint": _TOKEN_URL,
}


def _read_users(expecting_exception: bool = False):
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    catalog = CatalogBuilder().with_stream("users", SyncMode.full_refresh).build()
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

        output = _read_users()

    assert [record.record.data["id"] for record in output.records] == ["u1"]

    assert token_mock.call_count == 1
    token_request = token_mock.request_history[0]
    assert parse_qs(urlparse(token_request.url).query) == {
        "grant_type": ["account_credentials"],
        "account_id": ["test_account_id"],
    }
    assert token_request.headers["Authorization"] == f"Basic {expected_basic}"
    assert not token_request.body

    assert users_mock.call_count == 1
    assert users_mock.request_history[0].headers["Authorization"] == "Bearer test_access_token"


@pytest.mark.parametrize(
    "error_body",
    [
        pytest.param({"reason": "Invalid client_id or client_secret", "error": "invalid_client"}, id="invalid_client"),
        pytest.param({"reason": "Bad Request", "error": "invalid_request"}, id="invalid_account_id"),
    ],
)
def test_invalid_credentials_raise_config_error(error_body):
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, status_code=400, json=error_body)
        users_mock = mocker.get(_USERS_URL, json={"users": [], "next_page_token": ""})

        output = _read_users(expecting_exception=True)

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
