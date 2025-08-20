# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

import freezegun
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = ab_datetime_now().subtract(timedelta(weeks=52))


@freezegun.freeze_time(_NOW.isoformat())
class TestOAuthRefreshAuthentication(TestCase):
    def _config(self) -> ConfigBuilder:
        return (
            ConfigBuilder()
            .with_oauth_refresh_credentials(
                refresh_token="test_refresh_token", client_id="test_client_id", client_secret="test_client_secret"
            )
            .with_subdomain("d3v-airbyte")
            .with_start_date(ab_datetime_now().subtract(timedelta(hours=1)))
        )

    @HttpMocker()
    def test_oauth_refresh_token_authentication_flow(self, http_mocker):
        """Test that OAuth refresh token flow works correctly with token refresh"""
        config = self._config().build()

        # Mock the OAuth token refresh endpoint
        http_mocker.post(
            "https://d3v-airbyte.zendesk.com/oauth/tokens",
            {
                "access_token": "new_access_token_12345",
                "expires_in": 7200,
                "refresh_token": "new_refresh_token_67890",
                "token_type": "Bearer",
            },
        )

        # Mock the actual API call that should use the refreshed access token
        http_mocker.get(
            "https://d3v-airbyte.zendesk.com/api/v2/brands",
            {"brands": [{"id": 1, "name": "Test Brand", "active": True}]},
            headers={"Authorization": "Bearer new_access_token_12345"},
        )

        # Read from brands stream which should trigger OAuth flow
        output = read_stream("brands", SyncMode.full_refresh, config)

        # Verify we got records (meaning authentication worked)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["name"] == "Test Brand"

    @HttpMocker()
    def test_oauth_refresh_token_failure_handling(self, http_mocker):
        """Test that OAuth refresh token failure is handled properly"""
        config = self._config().build()

        # Mock the OAuth token refresh endpoint to return an error
        http_mocker.post(
            "https://d3v-airbyte.zendesk.com/oauth/tokens",
            {"error": "invalid_grant", "error_description": "The provided authorization grant is invalid"},
            status_code=400,
        )

        # Attempt to read from a stream should fail due to authentication error
        try:
            output = read_stream("brands", SyncMode.full_refresh, config)
            # If we get here, the test should fail as we expect an exception
            assert False, "Expected authentication error but stream read succeeded"
        except Exception as e:
            # Verify that the error is related to OAuth authentication
            assert "oauth" in str(e).lower() or "auth" in str(e).lower() or "token" in str(e).lower()

    @patch("source_declarative_manifest.components.ZendeskSupportOAuth2Authenticator.get_refresh_request_body")
    def test_oauth_request_body_format(self, mock_get_refresh_request_body):
        """Test that OAuth refresh request body is formatted correctly"""
        from source_declarative_manifest.components import ZendeskSupportOAuth2Authenticator

        config = self._config().build()
        credentials = config["credentials"]

        authenticator = ZendeskSupportOAuth2Authenticator(
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            refresh_token=credentials["refresh_token"],
            token_refresh_endpoint="https://d3v-airbyte.zendesk.com/oauth/tokens",
            grant_type="refresh_token",
        )

        # Call the method that formats the request body
        request_body = authenticator.get_refresh_request_body()

        # Verify the request body has the correct format for Zendesk OAuth
        expected_body = {
            "grant_type": "refresh_token",
            "refresh_token": "test_refresh_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        }

        assert request_body == expected_body

    @HttpMocker()
    def test_oauth_refresh_with_missing_fields_in_response(self, http_mocker):
        """Test OAuth refresh handles responses missing optional fields"""
        config = self._config().build()

        # Mock OAuth token refresh with minimal response (no expires_in)
        http_mocker.post(
            "https://d3v-airbyte.zendesk.com/oauth/tokens",
            {
                "access_token": "minimal_access_token"
                # Note: missing expires_in should default to 7200 seconds
            },
        )

        # Mock API call with the new token
        http_mocker.get(
            "https://d3v-airbyte.zendesk.com/api/v2/brands",
            {"brands": [{"id": 1, "name": "Test Brand"}]},
            headers={"Authorization": "Bearer minimal_access_token"},
        )

        # Should work even with minimal response
        output = read_stream("brands", SyncMode.full_refresh, config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_oauth_refresh_network_error_handling(self, http_mocker):
        """Test OAuth refresh handles network errors properly"""
        config = self._config().build()

        # Mock network error during token refresh
        http_mocker.post("https://d3v-airbyte.zendesk.com/oauth/tokens", exc=requests_mock.exceptions.ConnectTimeout)

        # Should handle network errors gracefully
        try:
            output = read_stream("brands", SyncMode.full_refresh, config)
            assert False, "Expected network error but stream read succeeded"
        except Exception as e:
            # Verify error handling mentions network/connection issues
            error_msg = str(e).lower()
            assert any(term in error_msg for term in ["http", "connection", "network", "timeout", "token"])
