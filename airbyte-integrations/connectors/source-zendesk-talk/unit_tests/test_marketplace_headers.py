# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the Zendesk Marketplace headers, which the connector sends on every request to Zendesk in Airbyte Cloud only."""

import logging
from copy import deepcopy
from typing import Any, Mapping
from urllib.parse import parse_qs

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


LOGGER = logging.getLogger("airbyte")
VOICE_API = "https://example.zendesk.com/api/v2/channels/voice"
TOKEN_URL = "https://example.zendesk.com/oauth/tokens"
MARKETPLACE_HEADERS = {
    "X-Zendesk-Marketplace-Name": "Airbyte",
    "X-Zendesk-Marketplace-Organization-Id": "REPLACE_WITH_ZENDESK_MARKETPLACE_ORGANIZATION_ID",
    "X-Zendesk-Marketplace-App-Id": "REPLACE_WITH_ZENDESK_MARKETPLACE_APP_ID",
}
OAUTH_REFRESH_CONFIG = {
    "subdomain": "example",
    "start_date": "2024-01-01T00:00:00Z",
    "credentials": {
        "auth_type": "oauth2_refresh",
        "client_id": "client",
        "client_secret": "secret",
        "refresh_token": "refresh",
        "access_token": "expired",
        "token_expiry_date": "2020-01-01T00:00:00Z",
    },
}
CONFIG_SHAPES = {
    "legacy_top_level_token": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "access_token": "token",
        "email": "a@example.com",
    },
    "api_token": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {"auth_type": "api_token", "email": "a@example.com", "api_token": "token"},
    },
    "legacy_oauth": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {"auth_type": "oauth2.0", "access_token": "token"},
    },
    "oauth_refresh": OAUTH_REFRESH_CONFIG,
}


def _set_edition(monkeypatch: pytest.MonkeyPatch, edition: str | None) -> None:
    if edition is None:
        monkeypatch.delenv("AIRBYTE_EDITION", raising=False)
    else:
        monkeypatch.setenv("AIRBYTE_EDITION", edition)


def _marketplace_headers(request: Any) -> Mapping[str, str]:
    return {name: value for name, value in request.headers.items() if name.lower().startswith("x-zendesk-marketplace")}


def _mock_zendesk(mocker: requests_mock.Mocker) -> None:
    mocker.post(TOKEN_URL, json={"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 172800})
    mocker.get(requests_mock.ANY, json={})
    mocker.get(f"{VOICE_API}/addresses", json={"addresses": [{"id": 1, "name": "Main"}]})


def _read_addresses(config: Mapping[str, Any]) -> list[Any]:
    config = deepcopy(config)  # a token refresh writes the new tokens into the config
    with requests_mock.Mocker() as mocker:
        _mock_zendesk(mocker)
        output = read(get_source(config), config, CatalogBuilder().with_stream("addresses", SyncMode.full_refresh).build())
        history = list(mocker.request_history)

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]
    return history


@pytest.mark.parametrize("edition", ["CLOUD", "cloud"])
@pytest.mark.parametrize("config", CONFIG_SHAPES.values(), ids=CONFIG_SHAPES.keys())
def test_cloud_sends_the_headers_on_data_requests_for_every_auth_type(
    monkeypatch: pytest.MonkeyPatch, config: Mapping[str, Any], edition: str
) -> None:
    _set_edition(monkeypatch, edition)

    data_requests = [request for request in _read_addresses(config) if request.method == "GET"]

    assert data_requests
    for request in data_requests:
        assert _marketplace_headers(request) == MARKETPLACE_HEADERS
        assert request.headers["Authorization"]


def test_cloud_sends_the_headers_on_the_token_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_edition(monkeypatch, "CLOUD")

    history = _read_addresses(OAUTH_REFRESH_CONFIG)

    refresh_requests = [request for request in history if request.url == TOKEN_URL]
    assert len(refresh_requests) == 1
    assert _marketplace_headers(refresh_requests[0]) == MARKETPLACE_HEADERS
    data_requests = [request for request in history if request.method == "GET"]
    assert data_requests
    assert all(request.headers["Authorization"] == "Bearer new-access" for request in data_requests)


def test_token_refresh_body_is_the_same_in_every_edition(monkeypatch: pytest.MonkeyPatch) -> None:
    bodies = {}
    for edition in ("CLOUD", "COMMUNITY"):
        _set_edition(monkeypatch, edition)
        (refresh_request,) = [request for request in _read_addresses(OAUTH_REFRESH_CONFIG) if request.url == TOKEN_URL]
        bodies[edition] = parse_qs(refresh_request.text)

    assert bodies["CLOUD"] == bodies["COMMUNITY"]
    assert bodies["CLOUD"] == {
        "grant_type": ["refresh_token"],
        "client_id": ["client"],
        "client_secret": ["secret"],
        "refresh_token": ["refresh"],
        "expires_in": ["172800"],
    }


@pytest.mark.parametrize("edition", ["COMMUNITY", "ENTERPRISE", "", None])
@pytest.mark.parametrize("config", CONFIG_SHAPES.values(), ids=CONFIG_SHAPES.keys())
def test_self_managed_sends_no_marketplace_header(monkeypatch: pytest.MonkeyPatch, config: Mapping[str, Any], edition: str | None) -> None:
    _set_edition(monkeypatch, edition)

    history = _read_addresses(config)

    assert history
    for request in history:
        assert _marketplace_headers(request) == {}


def test_cloud_sends_the_headers_on_check_and_on_every_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_edition(monkeypatch, "CLOUD")
    config = deepcopy(CONFIG_SHAPES["api_token"])

    with requests_mock.Mocker() as mocker:
        _mock_zendesk(mocker)
        source = get_source(config)
        status = source.check(LOGGER, config)
        stream_names = [stream.name for stream in source.discover(LOGGER, config).streams]
        catalog = CatalogBuilder()
        for stream_name in stream_names:
            catalog = catalog.with_stream(stream_name, SyncMode.full_refresh)
        read(get_source(config), config, catalog.build())
        history = list(mocker.request_history)

    assert status.status == Status.SUCCEEDED, status.message
    assert {"addresses", "ivrs", "ivr_menus", "ivr_routes", "phone_numbers"} <= set(stream_names)
    requested_paths = {request.path for request in history}
    # ivrs, ivr_menus and ivr_routes read the same path, so three streams count as one path.
    assert len(requested_paths) >= len(stream_names) - 2, requested_paths
    for request in history:
        assert _marketplace_headers(request) == MARKETPLACE_HEADERS, request.url
