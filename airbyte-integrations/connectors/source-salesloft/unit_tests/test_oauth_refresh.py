# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs

import requests_mock
from _helpers import get_source


def _oauth_config() -> dict:
    return {
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "configured-client-id",
            "client_secret": "configured-client-secret",
            "refresh_token": "configured-refresh-token",
            "access_token": "expired-access-token",
            "token_expiry_date": "2000-01-01T00:00:00Z",
        },
    }


def _authenticator(config: dict):
    source = get_source(config)
    stream = source.streams(config)[0]
    retriever = stream._stream_partition_generator._partition_factory._retriever
    return retriever.requester.authenticator


def test_oauth_refresh_succeeds_with_form_body_and_updates_config():
    config = _oauth_config()
    authenticator = _authenticator(config)

    with requests_mock.Mocker() as mocker:
        mocker.post(
            "https://accounts.salesloft.com/oauth/token",
            json={
                "access_token": "refreshed-access-token",
                "refresh_token": "refreshed-refresh-token",
                "expires_in": 3600,
            },
        )

        assert authenticator.get_access_token() == "refreshed-access-token"

        request = mocker.last_request
        assert request is not None
        assert request.url == "https://accounts.salesloft.com/oauth/token"
        assert parse_qs(request.text) == {
            "client_id": ["configured-client-id"],
            "client_secret": ["configured-client-secret"],
            "refresh_token": ["configured-refresh-token"],
            "grant_type": ["refresh_token"],
        }

    assert config["credentials"]["access_token"] == "refreshed-access-token"
    assert config["credentials"]["refresh_token"] == "refreshed-refresh-token"
    assert config["credentials"]["token_expiry_date"] != "2000-01-01T00:00:00Z"


def test_api_key_authenticator_uses_configured_token():
    config = {
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {"auth_type": "api_key", "api_key": "configured-api-key"},
    }

    authenticator = _authenticator(config)

    assert authenticator.token == "Bearer configured-api-key"
