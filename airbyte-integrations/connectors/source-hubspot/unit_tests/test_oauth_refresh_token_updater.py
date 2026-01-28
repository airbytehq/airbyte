#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Tests for OAuth2.0 refresh_token_updater functionality.

These tests verify that the refresh_token_updater configuration in the OAuth authenticator
works correctly, including token refresh when the access token is expired.
"""

import json
from datetime import timedelta

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import get_source


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_OAUTH_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

_CLIENT_ID = "test_client_id"
_CLIENT_SECRET = "test_client_secret"
_INITIAL_REFRESH_TOKEN = "initial_refresh_token"
_INITIAL_ACCESS_TOKEN = "initial_access_token"
_NEW_ACCESS_TOKEN = "new_access_token_after_refresh"


def _build_oauth_config(
    access_token: str,
    token_expiry_date: str,
) -> dict:
    """Build a config with OAuth credentials including token_expiry_date for refresh_token_updater."""
    return {
        "start_date": _START_DATE.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "client_id": _CLIENT_ID,
            "client_secret": _CLIENT_SECRET,
            "refresh_token": _INITIAL_REFRESH_TOKEN,
            "access_token": access_token,
            "token_expiry_date": token_expiry_date,
        },
    }


def _build_token_refresh_response_json(access_token: str, refresh_token: str, expires_in: int = 7200) -> str:
    """Build a JSON response string for the token refresh endpoint."""
    return json.dumps(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        }
    )


def _get_expired_token_expiry_date() -> str:
    """Return a token expiry date in the past to trigger refresh."""
    return (_NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_future_token_expiry_date() -> str:
    """Return a token expiry date in the future (valid token)."""
    return (_NOW + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_stream(stream_name: str, config: dict):
    """Helper to read a stream with the given config."""
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = get_source(config)
    return read(source, config, catalog, expecting_exception=False)


@pytest.mark.parametrize(
    "token_expiry_date,access_token,should_refresh",
    [
        pytest.param(
            _get_expired_token_expiry_date(),
            _INITIAL_ACCESS_TOKEN,
            True,
            id="expired_token_triggers_refresh",
        ),
        pytest.param(
            _get_future_token_expiry_date(),
            _INITIAL_ACCESS_TOKEN,
            False,
            id="valid_token_no_refresh",
        ),
    ],
)
@freezegun.freeze_time(_NOW.isoformat())
def test_oauth_refresh_token_updater(
    token_expiry_date: str,
    access_token: str,
    should_refresh: bool,
):
    """
    Test that refresh_token_updater correctly handles token refresh based on expiry.

    When the access token is expired (token_expiry_date in the past), the connector
    should call the token refresh endpoint before making API requests.

    When the access token is still valid (token_expiry_date in the future), the
    connector should use the existing token without refreshing.
    """
    config = _build_oauth_config(
        access_token=access_token,
        token_expiry_date=token_expiry_date,
    )

    with HttpMocker() as http_mocker:
        # Register OAuth token refresh endpoint directly on requests_mock
        # to bypass HttpMocker's JSON-only body matcher (OAuth uses form-urlencoded)
        oauth_mock = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _INITIAL_REFRESH_TOKEN),
            status_code=200,
        )

        # The token used in API requests depends on whether refresh happened
        expected_token = _NEW_ACCESS_TOKEN if should_refresh else _INITIAL_ACCESS_TOKEN

        # Mock the schemas endpoint (called during stream discovery)
        http_mocker._mocker.get(
            "https://api.hubapi.com/crm/v3/schemas",
            json={"results": []},
            status_code=200,
            request_headers={"Authorization": f"Bearer {expected_token}"},
        )

        # Mock the owners endpoint (a simple stream to test with)
        http_mocker._mocker.get(
            "https://api.hubapi.com/crm/v3/owners/",
            json={"results": []},
            status_code=200,
            request_headers={"Authorization": f"Bearer {expected_token}"},
        )

        output = _read_stream("owners", config)

        # Verify token refresh was called (or not) based on expiry
        if should_refresh:
            assert oauth_mock.call_count >= 1, "Token refresh should have been called for expired token"
        else:
            assert oauth_mock.call_count == 0, "Token refresh should not be called for valid token"
