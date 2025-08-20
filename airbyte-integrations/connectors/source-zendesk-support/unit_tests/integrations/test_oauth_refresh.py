# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest.mock import patch, MagicMock

import pytest
import requests

from .config import ConfigBuilder


def _get_config():
    """Helper function to build test config"""
    return (
        ConfigBuilder()
        .with_oauth_refresh_credentials(
            refresh_token="test_refresh_token", client_id="test_client_id", client_secret="test_client_secret"
        )
        .with_subdomain("d3v-airbyte")
        .build()
    )


def test_oauth_authenticator_direct_token_refresh(components_module):
    """Test OAuth authenticator refresh_access_token method directly like successful connectors do"""
    
    # Create authenticator instance
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id="test_client_id",
        client_secret="test_client_secret", 
        refresh_token="test_refresh_token",
        token_refresh_endpoint="https://d3v-airbyte.zendesk.com/oauth/tokens",
        config={"subdomain": "d3v-airbyte"},
        parameters={},
    )
    
    # Mock successful requests.request call
    with patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_access_token_12345",
            "expires_in": 7200,
            "refresh_token": "new_refresh_token_67890",
            "token_type": "Bearer",
        }
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        # Call refresh_access_token directly
        access_token, expires_in = authenticator.refresh_access_token()
        
        # Verify results
        assert access_token == "new_access_token_12345"
        assert expires_in == 7200
        
        # Verify request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://d3v-airbyte.zendesk.com/oauth/tokens",
            json={
                "grant_type": "refresh_token",
                "refresh_token": "test_refresh_token",
                "client_id": "test_client_id", 
                "client_secret": "test_client_secret",
            },
            headers={"Content-Type": "application/json"},
        )


def test_oauth_authenticator_direct_token_refresh_error(components_module):
    """Test OAuth authenticator handles refresh errors properly"""
    
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token", 
        token_refresh_endpoint="https://d3v-airbyte.zendesk.com/oauth/tokens",
        config={"subdomain": "d3v-airbyte"},
        parameters={},
    )
    
    # Mock failed requests.request call 
    with patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_request.return_value = mock_response
        
        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            authenticator.refresh_access_token()
        
        assert "HTTP error while refreshing Zendesk access token" in str(exc_info.value)


def test_oauth_request_body_format():
    """Test that the OAuth request body contains the correct fields and format"""
    config = _get_config()

    # Validate that the config has the expected OAuth refresh structure
    assert config["credentials"]["credentials"] == "oauth2.0_refresh"
    assert "refresh_token" in config["credentials"]
    assert "client_id" in config["credentials"]
    assert "client_secret" in config["credentials"]
    
    # Validate config structure for the new OAuth flow
    expected_keys = {"refresh_token", "client_id", "client_secret", "credentials"}
    actual_keys = set(config["credentials"].keys())
    assert expected_keys.issubset(actual_keys), f"Missing OAuth fields. Expected: {expected_keys}, Got: {actual_keys}"


def test_oauth_authenticator_missing_access_token_handling(components_module):
    """Test OAuth authenticator defaults expires_in when missing from response"""
    
    authenticator = components_module.ZendeskSupportOAuth2Authenticator(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
        token_refresh_endpoint="https://d3v-airbyte.zendesk.com/oauth/tokens",
        config={"subdomain": "d3v-airbyte"},
        parameters={},
    )
    
    # Mock response without expires_in field
    with patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "minimal_access_token"
            # Note: missing expires_in should default to 7200 seconds
        }
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        # Should work and default expires_in to 7200
        access_token, expires_in = authenticator.refresh_access_token()
        assert access_token == "minimal_access_token"
        assert expires_in == 7200  # Default value