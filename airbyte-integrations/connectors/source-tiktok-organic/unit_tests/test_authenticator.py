#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest

from source_tiktok_organic.components import TiktokOrganicAuthenticator


CONFIG = {
    "client_key": "test_client_key",
    "client_secret": "test_client_secret",
    "refresh_token": "test_refresh_token",
    "open_id": "test_open_id",
}

MOCK_TOKEN_RESPONSE = {
    "access_token": "mock_access_token_12345",
    "token_type": "Bearer",
    "expires_in": 86400,
}


def make_authenticator() -> TiktokOrganicAuthenticator:
    """Construct the authenticator the same way the CDK does it."""
    return TiktokOrganicAuthenticator(
        config=CONFIG,
        client_key=CONFIG["client_key"],
        client_secret=CONFIG["client_secret"],
        refresh_token=CONFIG["refresh_token"],
        parameters={},
    )


def test_authenticator_stores_credentials():
    auth = make_authenticator()
    assert auth.client_key == "test_client_key"
    assert auth.client_secret == "test_client_secret"
    assert auth.refresh_token == "test_refresh_token"


def test_get_token_calls_tiktok_oauth(requests_mock):
    requests_mock.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        json=MOCK_TOKEN_RESPONSE,
    )
    auth = make_authenticator()
    token = auth.get_token()
    assert token == "mock_access_token_12345"


def test_get_token_sends_correct_payload(requests_mock):
    adapter = requests_mock.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        json=MOCK_TOKEN_RESPONSE,
    )
    auth = make_authenticator()
    auth.get_token()

    sent_body = adapter.last_request.text
    assert "client_key=test_client_key" in sent_body
    assert "client_secret=test_client_secret" in sent_body
    assert "refresh_token=test_refresh_token" in sent_body
    assert "grant_type=refresh_token" in sent_body


def test_get_auth_header(requests_mock):
    requests_mock.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        json=MOCK_TOKEN_RESPONSE,
    )
    auth = make_authenticator()
    header = auth.get_auth_header()
    assert header == {"Access-Token": "mock_access_token_12345"}


def test_token_is_cached(requests_mock):
    requests_mock.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        json=MOCK_TOKEN_RESPONSE,
    )
    auth = make_authenticator()
    _ = auth.get_token()
    _ = auth.get_token()
    assert requests_mock.call_count == 1


def test_api_error_raises_exception(requests_mock):
    requests_mock.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        json={"error": "invalid_grant", "error_description": "Refresh token is expired"},
    )
    auth = make_authenticator()
    with pytest.raises(RuntimeError, match="Refresh token is expired"):
        auth.get_token()


def test_http_error_raises_exception(requests_mock):
    requests_mock.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        status_code=400,
        text="Bad Request",
    )
    auth = make_authenticator()
    with pytest.raises(Exception):
        auth.get_token()
