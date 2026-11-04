# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs

import pytest
import requests_mock as requests_mock_module

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
TOKEN_URL = "https://api.outreach.io/oauth/token"
MAILINGS_URL = "https://api.outreach.io/api/v2/mailings"
NEXT_PAGE_URL = f"{MAILINGS_URL}?page%5Bafter%5D=cursor-1"
CONFIG = {
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "refresh-0",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2024-01-01T00:00:00Z",
}
EXPIRED_ACCESS_TOKEN_BODY = {
    "errors": [
        {
            "id": "expiredAccessToken",
            "title": "Expired Access Token",
            "detail": "Please get a new access token and try again.",
        }
    ]
}


class FakeOutreach:
    """Outreach rotates the refresh token on every refresh and only the most recent one is valid."""

    def __init__(self, expire_after_first_page: bool = True, reject_all_tokens: bool = False):
        self.valid_refresh_token = CONFIG["refresh_token"]
        self.valid_access_token = None
        self.refresh_tokens_sent = []
        self.api_requests = []
        self.expire_after_first_page = expire_after_first_page
        self.reject_all_tokens = reject_all_tokens
        self._issued = 0

    def token(self, request, context):
        sent = parse_qs(request.body)["refresh_token"][0]
        self.refresh_tokens_sent.append(sent)
        if sent != self.valid_refresh_token:
            context.status_code = 400
            return {"error": "invalid_grant", "error_description": "The provided authorization grant is invalid."}
        self._issued += 1
        self.valid_access_token = f"access-{self._issued}"
        self.valid_refresh_token = f"refresh-{self._issued}"
        return {
            "access_token": self.valid_access_token,
            "refresh_token": self.valid_refresh_token,
            "expires_in": 7200,
            "token_type": "bearer",
        }

    def _authorized(self, request) -> bool:
        return not self.reject_all_tokens and request.headers.get("Authorization") == f"Bearer {self.valid_access_token}"

    def mailings(self, request, context):
        self.api_requests.append((request.url, request.headers.get("Authorization")))
        if "page[after]" in request.qs:
            return self.next_page(request, context)
        return self.first_page(request, context)

    def first_page(self, request, context):
        if not self._authorized(request):
            context.status_code = 401
            return EXPIRED_ACCESS_TOKEN_BODY
        if self.expire_after_first_page:
            # The access token expires while the stream is still paginating.
            self.valid_access_token = None
        return {
            "data": [{"id": 1, "attributes": {"updatedAt": "2024-02-01T00:00:00.000Z"}}],
            "links": {"next": NEXT_PAGE_URL},
        }

    def next_page(self, request, context):
        if not self._authorized(request):
            context.status_code = 401
            return EXPIRED_ACCESS_TOKEN_BODY
        return {"data": [{"id": 2, "attributes": {"updatedAt": "2024-02-02T00:00:00.000Z"}}], "links": {}}


def _read_mailings(outreach: FakeOutreach, config=None):
    config = deepcopy(config or CONFIG)
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
    with requests_mock_module.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=outreach.token)
        mocker.get(MAILINGS_URL, json=outreach.mailings)
        return read(source, config, catalog, expecting_exception=True)


def test_expired_access_token_mid_sync_is_refreshed_with_rotated_refresh_token():
    outreach = FakeOutreach()

    output = _read_mailings(outreach)

    assert not output.errors, [error.trace.error.internal_message for error in output.errors]
    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert outreach.refresh_tokens_sent == ["refresh-0", "refresh-1"]


def _control_message_configs(stdout: str):
    """The OAuth authenticator prints CONNECTOR_CONFIG control messages straight to stdout."""
    messages = [json.loads(line) for line in stdout.splitlines() if line.startswith("{")]
    return [message["control"]["connectorConfig"]["config"] for message in messages if message.get("type") == Type.CONTROL.value]


def test_rotated_refresh_token_is_persisted_for_the_next_sync(capsys):
    outreach = FakeOutreach()

    _read_mailings(outreach)

    updated_configs = _control_message_configs(capsys.readouterr().out)
    assert [config["refresh_token"] for config in updated_configs] == ["refresh-1", "refresh-2"]
    updated_config = updated_configs[-1]
    assert updated_config["refresh_token"] == "refresh-2"
    assert updated_config["access_token"] == "access-2"
    assert updated_config["token_expiry_date"]

    next_sync_outreach = FakeOutreach(expire_after_first_page=False)
    next_sync_outreach.valid_refresh_token = updated_config["refresh_token"]
    next_sync_config = {**CONFIG, "refresh_token": updated_config["refresh_token"]}
    next_output = _read_mailings(next_sync_outreach, next_sync_config)

    assert not next_output.errors
    assert next_sync_outreach.refresh_tokens_sent == ["refresh-2"]


def test_access_token_rejected_after_refresh_fails_as_config_error():
    outreach = FakeOutreach(expire_after_first_page=False, reject_all_tokens=True)

    output = _read_mailings(outreach)

    assert output.errors
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
    assert outreach.refresh_tokens_sent == ["refresh-0", "refresh-1"]
