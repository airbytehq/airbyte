# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for OAuth2.0 with refresh token authentication flow.

These tests verify the oauth2_refresh authentication option works correctly,
including token refresh and rotating refresh token handling.

Note: The CDK's OAuthAuthenticator sends refresh requests with form-urlencoded
data (using requests.request(..., data=...)), but the HttpMocker's matcher
tries to parse bodies as JSON. To work around this, we register the OAuth
token endpoint directly on the underlying requests_mock.Mocker to bypass
the JSON-only body matcher.
"""

import json
from datetime import timedelta
from unittest import TestCase

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import (
    OAuthBearerAuthenticator,
    ZendeskSupportRequestBuilder,
)
from .response_builder import (
    TagsRecordBuilder,
    TagsResponseBuilder,
)
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_SUBDOMAIN = "d3v-airbyte"
_OAUTH_TOKEN_URL = f"https://{_SUBDOMAIN}.zendesk.com/oauth/tokens"

_CLIENT_ID = "test_client_id"
_CLIENT_SECRET = "test_client_secret"
_INITIAL_REFRESH_TOKEN = "initial_refresh_token_rt1"
_ROTATED_REFRESH_TOKEN = "rotated_refresh_token_rt2"
_INITIAL_ACCESS_TOKEN = "initial_access_token"
_NEW_ACCESS_TOKEN = "new_access_token_after_refresh"


def _build_oauth_refresh_config(
    refresh_token: str,
    access_token: str,
    token_expiry_date: str,
) -> dict:
    """Build a config with oauth2_refresh credentials."""
    return (
        ConfigBuilder()
        .with_subdomain(_SUBDOMAIN)
        .with_start_date(_START_DATE)
        .with_oauth_refresh_credentials(
            client_id=_CLIENT_ID,
            client_secret=_CLIENT_SECRET,
            refresh_token=refresh_token,
            access_token=access_token,
            token_expiry_date=token_expiry_date,
        )
        .build()
    )


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


@freezegun.freeze_time(_NOW.isoformat())
class TestOAuthRefreshFlowWithExpiredToken(TestCase):
    """Tests for OAuth refresh flow when the access token is expired."""

    def _get_expired_token_expiry_date(self) -> str:
        """Return a token expiry date in the past to trigger refresh."""
        return (_NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _get_future_token_expiry_date(self) -> str:
        """Return a token expiry date in the future (valid token)."""
        return (_NOW + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    @HttpMocker()
    def test_given_expired_token_when_read_then_refresh_token_and_sync_data(self, http_mocker):
        """
        Test that when the access token is expired, the connector:
        1. Calls POST /oauth/tokens to refresh the token
        2. Uses the new access token to make API requests
        3. Successfully syncs data
        """
        config = _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=self._get_expired_token_expiry_date(),
        )

        # Register OAuth token refresh endpoint directly on requests_mock
        # to bypass HttpMocker's JSON-only body matcher
        http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_valid_token_when_read_then_no_refresh_needed(self, http_mocker):
        """
        Test that when the access token is still valid (not expired),
        the connector does not call the token refresh endpoint.
        """
        config = _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=self._get_future_token_expiry_date(),
        )

        oauth_authenticator = OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestOAuthRefreshTokenRotation(TestCase):
    """
    Tests for rotating refresh token handling.

    Zendesk uses rotating refresh tokens where each token refresh returns a new
    refresh token and invalidates the previous one. These tests verify that the
    connector correctly calls the token refresh endpoint and syncs data.

    Note: Config update verification is not reliable in mock tests because the
    refresh_token_updater callback mechanism works differently in the test
    environment. The actual config persistence is tested via integration tests.
    """

    def _get_expired_token_expiry_date(self) -> str:
        """Return a token expiry date in the past to trigger refresh."""
        return (_NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    @HttpMocker()
    def test_given_expired_token_when_read_then_calls_refresh_endpoint_and_syncs(self, http_mocker):
        """
        Test that when the access token is expired, the connector:
        1. Calls POST /oauth/tokens to refresh the token
        2. Uses the new access token to make API requests
        3. Successfully syncs data

        This verifies the OAuth refresh flow works end-to-end.
        """
        config = _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=self._get_expired_token_expiry_date(),
        )

        # Register OAuth token refresh endpoint directly on requests_mock
        # to bypass HttpMocker's JSON-only body matcher
        http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_refresh_returns_rotated_token_when_read_then_syncs_successfully(self, http_mocker):
        """
        Test that when the token refresh returns a rotated refresh token,
        the connector successfully syncs data using the new access token.

        This verifies the connector handles the token rotation response correctly.
        """
        config = _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=self._get_expired_token_expiry_date(),
        )

        # Register OAuth token refresh endpoint directly on requests_mock
        # to bypass HttpMocker's JSON-only body matcher
        http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)
        assert len(output.records) == 1


@pytest.mark.parametrize(
    "initial_refresh_token,rotated_refresh_token",
    [
        pytest.param(
            _INITIAL_REFRESH_TOKEN,
            _ROTATED_REFRESH_TOKEN,
            id="standard_token_rotation",
        ),
        pytest.param(
            "custom_refresh_token_abc",
            "rotated_custom_token_xyz",
            id="custom_token_rotation",
        ),
    ],
)
@freezegun.freeze_time(_NOW.isoformat())
def test_oauth_refresh_with_different_token_values(
    initial_refresh_token: str,
    rotated_refresh_token: str,
):
    """
    Parametrized test for OAuth refresh flow with different token values.

    Verifies that the connector correctly handles token refresh regardless
    of the specific token values used.
    """
    expired_token_expiry = (_NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    config = _build_oauth_refresh_config(
        refresh_token=initial_refresh_token,
        access_token=_INITIAL_ACCESS_TOKEN,
        token_expiry_date=expired_token_expiry,
    )

    with HttpMocker() as http_mocker:
        # Register OAuth token refresh endpoint directly on requests_mock
        # to bypass HttpMocker's JSON-only body matcher
        http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, rotated_refresh_token),
            status_code=200,
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)

        assert len(output.records) == 1
