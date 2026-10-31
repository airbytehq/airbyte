# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs

import pytest
import requests_mock

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@pytest.fixture(autouse=True)
def disable_retry_backoff(monkeypatch):
    monkeypatch.setattr("backoff._sync.time.sleep", lambda _: None)


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
TOKEN_URL = "https://api.outreach.io/oauth/token"
MAILINGS_URL = "https://api.outreach.io/api/v2/mailings"
PAGE_2_URL = f"{MAILINGS_URL}?page%5Bafter%5D=cursor-2"


def _config() -> dict:
    return {
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-token-0",
        "redirect_uri": "https://example.com/callback",
        "start_date": "2024-01-01T00:00:00Z",
    }


def _mailings_page(record_id: int, next_url: str = None) -> dict:
    return {
        "data": [
            {
                "id": record_id,
                "type": "mailing",
                "attributes": {"updatedAt": "2024-02-01T00:00:00.000Z"},
                "relationships": {},
            }
        ],
        "links": {"next": next_url} if next_url else {},
    }


class OutreachTokenServer:
    """Mimics Outreach OAuth: every refresh rotates the refresh token and only the latest one is accepted."""

    def __init__(self, expires_in: int):
        self.expires_in = expires_in
        self.issued = 0
        self.refresh_tokens_sent = []

    @property
    def current_access_token(self) -> str:
        return f"access-token-{self.issued}"

    def __call__(self, request, context):
        sent = parse_qs(request.text).get("refresh_token", [None])[0]
        self.refresh_tokens_sent.append(sent)
        if sent != f"refresh-token-{self.issued}":
            context.status_code = 400
            return {"error": "invalid_grant", "error_description": "The provided authorization grant is invalid, expired or revoked."}
        self.issued += 1
        return {
            "access_token": self.current_access_token,
            "refresh_token": f"refresh-token-{self.issued}",
            "token_type": "bearer",
            "expires_in": self.expires_in,
        }


def _expired_access_token(context, body: dict | None = None) -> dict:
    context.status_code = 401
    if body is None:
        body = {
            "errors": [
                {
                    "id": "expiredAccessToken",
                    "title": "Expired Access Token",
                    "detail": "Please get a new access token and try again.",
                }
            ]
        }
    return body


def _read_mailings(config: dict):
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
    return read(source, config, catalog)


def test_rotated_refresh_token_is_used_for_next_refresh_and_persisted():
    token_server = OutreachTokenServer(expires_in=0)

    def mailings(request, context):
        if request.headers["Authorization"] != f"Bearer {token_server.current_access_token}":
            return _expired_access_token(context)
        if "page%5Bafter%5D=cursor-2" in request.url or "page[after]=cursor-2" in request.url:
            return _mailings_page(2)
        return _mailings_page(1, PAGE_2_URL)

    with requests_mock.Mocker() as m:
        m.post(TOKEN_URL, json=token_server)
        m.get(requests_mock.ANY, json=mailings)
        output = _read_mailings(_config())

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert token_server.refresh_tokens_sent[:2] == ["refresh-token-0", "refresh-token-1"]
    control_messages = output.get_message_by_types([Type.CONTROL])
    assert control_messages
    persisted_config = control_messages[-1].control.connectorConfig.config
    assert persisted_config["refresh_token"] == f"refresh-token-{token_server.issued}"
    assert persisted_config["access_token"] == token_server.current_access_token
    assert "token_expiry_date" in persisted_config


@pytest.mark.parametrize(
    "error_body",
    [
        {
            "errors": [
                {
                    "id": "expiredAccessToken",
                    "title": "Expired Access Token",
                    "detail": "Please get a new access token and try again.",
                }
            ]
        },
        {
            "id": "expiredAccessToken",
            "title": "Expired Access Token",
            "detail": "Please get a new access token and try again.",
        },
    ],
    ids=["json-api-error", "top-level-error"],
)
def test_expired_access_token_response_refreshes_token_and_retries(error_body):
    token_server = OutreachTokenServer(expires_in=7200)
    page_2_attempts = []

    def mailings(request, context):
        if "page%5Bafter%5D=cursor-2" in request.url or "page[after]=cursor-2" in request.url:
            page_2_attempts.append(request.headers["Authorization"])
            # Outreach expires the first access token before the connector's computed expiry date.
            if request.headers["Authorization"] == "Bearer access-token-1":
                return _expired_access_token(context, error_body)
            return _mailings_page(2)
        return _mailings_page(1, PAGE_2_URL)

    with requests_mock.Mocker() as m:
        m.post(TOKEN_URL, json=token_server)
        m.get(requests_mock.ANY, json=mailings)
        output = _read_mailings(_config())

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert token_server.refresh_tokens_sent == ["refresh-token-0", "refresh-token-1"]
    assert page_2_attempts == ["Bearer access-token-1", "Bearer access-token-2"]


def test_other_401_is_not_retried_and_is_config_error():
    token_server = OutreachTokenServer(expires_in=7200)

    def mailings(request, context):
        context.status_code = 401
        return {
            "errors": [
                {
                    "id": "unauthorizedOauthScope",
                    "title": "Unauthorized OAuth Scope",
                    "detail": "Your access token does not have the required scope.",
                }
            ]
        }

    with requests_mock.Mocker() as m:
        m.post(TOKEN_URL, json=token_server)
        m.get(requests_mock.ANY, json=mailings)
        output = _read_mailings(_config())

    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert token_server.refresh_tokens_sent == ["refresh-token-0"]


def test_revoked_refresh_token_is_reported_as_config_error():
    with requests_mock.Mocker() as m:
        m.post(
            TOKEN_URL,
            status_code=400,
            json={"error": "invalid_grant", "error_description": "The provided authorization grant is invalid, expired or revoked."},
        )
        output = _read_mailings(_config())

    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
