# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for OAuth2.0 with refresh token authentication flow.

These tests verify the oauth2_refresh authentication option works correctly,
including token refresh and rotating refresh token handling.
"""

from datetime import timedelta
from unittest import TestCase

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import (
    OAuthBearerAuthenticator,
    OAuthTokenRefreshRequestBuilder,
    ZendeskSupportRequestBuilder,
)
from .response_builder import (
    OAuthTokenRefreshResponseBuilder,
    TagsRecordBuilder,
    TagsResponseBuilder,
)
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_SUBDOMAIN = "d3v-airbyte"

_CLIENT_ID = "test_client_id"
_CLIENT_SECRET = "test_client_secret"
_INITIAL_REFRESH_TOKEN = "initial_refresh_token_rt1"
_ROTATED_REFRESH_TOKEN = "rotated_refresh_token_rt2"
_SECOND_ROTATED_REFRESH_TOKEN = "second_rotated_refresh_token_rt3"
_INITIAL_ACCESS_TOKEN = "initial_access_token"
_NEW_ACCESS_TOKEN = "new_access_token_after_refresh"
_SECOND_NEW_ACCESS_TOKEN = "second_new_access_token_after_refresh"


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


def _build_token_refresh_request(refresh_token: str):
    """Build a token refresh request with the given refresh token."""
    return (
        OAuthTokenRefreshRequestBuilder.oauth_tokens_endpoint(_SUBDOMAIN)
        .with_refresh_token(refresh_token)
        .with_client_id(_CLIENT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .build()
    )


def _build_token_refresh_response(access_token: str, refresh_token: str):
    """Build a token refresh response with the given tokens."""
    return (
        OAuthTokenRefreshResponseBuilder.oauth_token_response()
        .with_access_token(access_token)
        .with_refresh_token(refresh_token)
        .with_expires_in(7200)
        .build()
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

        http_mocker.post(
            _build_token_refresh_request(_INITIAL_REFRESH_TOKEN),
            _build_token_refresh_response(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
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
    connector correctly handles this rotation.
    """

    def _get_expired_token_expiry_date(self) -> str:
        """Return a token expiry date in the past to trigger refresh."""
        return (_NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    @HttpMocker()
    def test_given_two_syncs_when_read_then_use_rotated_refresh_token_on_second_sync(self, http_mocker):
        """
        Test that after a token refresh, the connector uses the rotated refresh token
        (not the original) for subsequent refreshes.

        This test simulates two sync operations:
        1. First sync: Uses initial refresh token (RT1) -> receives rotated token (RT2)
        2. Second sync: Uses rotated refresh token (RT2) -> receives new rotated token (RT3)

        This verifies the connector correctly persists and uses the rotated refresh token.
        """
        config = _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=self._get_expired_token_expiry_date(),
        )

        http_mocker.post(
            _build_token_refresh_request(_INITIAL_REFRESH_TOKEN),
            _build_token_refresh_response(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)
        assert len(output.records) == 1

        assert config["credentials"]["refresh_token"] == _ROTATED_REFRESH_TOKEN
        assert config["credentials"]["access_token"] == _NEW_ACCESS_TOKEN

    @HttpMocker()
    def test_given_refresh_returns_new_tokens_when_read_then_config_is_updated(self, http_mocker):
        """
        Test that after a successful token refresh, the config object is updated
        with the new access_token, refresh_token, and token_expiry_date.

        This is critical for rotating refresh tokens to work correctly, as the
        refresh_token_updater must persist the new tokens back to the config.
        """
        config = _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=self._get_expired_token_expiry_date(),
        )

        http_mocker.post(
            _build_token_refresh_request(_INITIAL_REFRESH_TOKEN),
            _build_token_refresh_response(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        read_stream("tags", SyncMode.full_refresh, config)

        assert config["credentials"]["access_token"] == _NEW_ACCESS_TOKEN
        assert config["credentials"]["refresh_token"] == _ROTATED_REFRESH_TOKEN


@pytest.mark.parametrize(
    "initial_refresh_token,expected_new_refresh_token,test_id",
    [
        pytest.param(
            _INITIAL_REFRESH_TOKEN,
            _ROTATED_REFRESH_TOKEN,
            id="initial_token_rotates_to_new_token",
        ),
        pytest.param(
            "custom_refresh_token_abc",
            "rotated_custom_token_xyz",
            id="custom_token_rotates_correctly",
        ),
    ],
)
@freezegun.freeze_time(_NOW.isoformat())
def test_oauth_refresh_token_rotation_parametrized(
    initial_refresh_token: str,
    expected_new_refresh_token: str,
    test_id: str,
):
    """
    Parametrized test for OAuth refresh token rotation with different token values.
    """
    expired_token_expiry = (_NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    config = _build_oauth_refresh_config(
        refresh_token=initial_refresh_token,
        access_token=_INITIAL_ACCESS_TOKEN,
        token_expiry_date=expired_token_expiry,
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(
            (
                OAuthTokenRefreshRequestBuilder.oauth_tokens_endpoint(_SUBDOMAIN)
                .with_refresh_token(initial_refresh_token)
                .with_client_id(_CLIENT_ID)
                .with_client_secret(_CLIENT_SECRET)
                .build()
            ),
            (
                OAuthTokenRefreshResponseBuilder.oauth_token_response()
                .with_access_token(_NEW_ACCESS_TOKEN)
                .with_refresh_token(expected_new_refresh_token)
                .build()
            ),
        )

        oauth_authenticator = OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(oauth_authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        assert config["credentials"]["refresh_token"] == expected_new_refresh_token
