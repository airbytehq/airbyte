import pytest
from unittest.mock import patch, MagicMock

from source_microsoft_sharepoint.sharepoint_client import SourceMicrosoftSharePointClient
from airbyte_cdk import AirbyteTracedException, FailureType
from office365.runtime.auth.token_response import TokenResponse


def create_mock_config():
    """Helper function to create a properly configured mock config object."""
    mock_credentials = MagicMock()
    mock_credentials.client_id = "test-client-id"
    mock_credentials.tenant_id = "test-tenant-id"
    mock_credentials.client_secret = "test-client-secret"
    mock_credentials.refresh_token = None

    mock_config = MagicMock()
    mock_config.credentials = mock_credentials
    return mock_config


def test_client_property_initializes_graph_client_when_not_exists():
    """Test that client property initializes a new GraphClient when _client is None."""
    with (
        patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication") as mock_confidential_client,
        patch("source_microsoft_sharepoint.sharepoint_client.GraphClient") as mock_graph_client,
    ):
        mock_config = create_mock_config()
        client = SourceMicrosoftSharePointClient(mock_config)
        assert client._client is None

        result = client.client

        mock_graph_client.assert_called_once_with(client._get_access_token)
        assert result == mock_graph_client.return_value
        assert client._client == mock_graph_client.return_value


def test_access_token_property():
    """Test access_token property returns the token from _get_access_token."""
    with (
        patch.object(SourceMicrosoftSharePointClient, "_get_access_token") as mock_get_access_token,
        patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication"),
    ):
        # Setup
        mock_config = create_mock_config()
        client = SourceMicrosoftSharePointClient(mock_config)

        token_value = "test-access-token-123"
        mock_get_access_token.return_value = {"access_token": token_value, "other_field": "value"}

        # Test
        result = client.access_token

        # Assert
        mock_get_access_token.assert_called_once_with()
        assert result == token_value


def test_get_token_response_object_wrapper():
    """Test get_token_response_object_wrapper returns a function that provides a TokenResponse object."""
    with (
        patch.object(SourceMicrosoftSharePointClient, "_get_access_token") as mock_get_access_token,
        patch("source_microsoft_sharepoint.sharepoint_client.TokenResponse") as mock_token_response,
        patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication"),
    ):
        # Setup
        mock_config = create_mock_config()
        client = SourceMicrosoftSharePointClient(mock_config)

        tenant_prefix = "test-tenant"
        token_data = {"access_token": "test-token", "expires_in": 3600}
        mock_get_access_token.return_value = token_data

        # Test
        token_func = client.get_token_response_object_wrapper(tenant_prefix)
        result = token_func()

        # Assert
        mock_get_access_token.assert_called_once_with(tenant_prefix=tenant_prefix)
        mock_token_response.from_json.assert_called_once_with(token_data)
        assert result == mock_token_response.from_json.return_value


def test_get_access_token_with_client_credentials():
    """Test _get_access_token acquires token using client credentials when no refresh token exists."""
    with (
        patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication") as mock_confidential_client,
        patch.object(SourceMicrosoftSharePointClient, "_get_scope") as mock_get_scope,
    ):
        # Setup
        mock_config = create_mock_config()
        client = SourceMicrosoftSharePointClient(mock_config)

        test_scope = ["https://graph.microsoft.com/.default"]
        mock_get_scope.return_value = test_scope

        expected_token = {"access_token": "test_access_token", "other_field": "value"}
        mock_msal_app = mock_confidential_client.return_value
        mock_msal_app.acquire_token_for_client.return_value = expected_token

        # Test
        result = client._get_access_token()

        # Assert
        mock_get_scope.assert_called_once_with(None)
        mock_msal_app.acquire_token_for_client.assert_called_once_with(scopes=test_scope)
        assert result == expected_token


def test_get_access_token_with_refresh_token():
    """Test _get_access_token uses refresh token when available."""
    with (
        patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication") as mock_confidential_client,
        patch.object(SourceMicrosoftSharePointClient, "_get_scope") as mock_get_scope,
    ):
        # Setup
        mock_config = create_mock_config()
        refresh_token = "test_refresh_token"
        mock_config.credentials.refresh_token = refresh_token
        client = SourceMicrosoftSharePointClient(mock_config)

        test_scope = ["https://tenant-admin.sharepoint.com/.default"]
        mock_get_scope.return_value = test_scope

        expected_token = {"access_token": "test_access_token", "other_field": "value"}
        mock_msal_app = mock_confidential_client.return_value
        mock_msal_app.acquire_token_by_refresh_token.return_value = expected_token

        tenant_prefix = "tenant"

        # Test
        result = client._get_access_token(tenant_prefix)

        # Assert
        mock_get_scope.assert_called_once_with(tenant_prefix)
        mock_msal_app.acquire_token_by_refresh_token.assert_called_once_with(refresh_token, scopes=test_scope)
        assert result == expected_token


def test_get_access_token_raises_error_when_token_acquisition_fails():
    """Test _get_access_token raises AirbyteTracedException when token acquisition fails."""
    with (
        patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication") as mock_confidential_client,
        patch.object(SourceMicrosoftSharePointClient, "_get_scope") as mock_get_scope,
    ):
        # Setup
        mock_config = create_mock_config()
        client = SourceMicrosoftSharePointClient(mock_config)

        error_response = {"error": "invalid_client", "error_description": "Client authentication failed"}
        mock_msal_app = mock_confidential_client.return_value
        mock_msal_app.acquire_token_for_client.return_value = error_response

        # Test & Assert
        with pytest.raises(AirbyteTracedException):
            client._get_access_token()


def test_get_scope_with_tenant_prefix():
    """Test _get_scope returns correct scope when tenant_prefix is provided."""
    tenant_name = "contoso"
    expected_scope = [f"https://{tenant_name}-admin.sharepoint.com/.default"]

    result = SourceMicrosoftSharePointClient._get_scope(tenant_prefix=tenant_name)

    assert result == expected_scope


def test_get_scope_without_tenant_prefix():
    """Test _get_scope returns default graph scope when tenant_prefix is not provided."""
    expected_scope = ["https://graph.microsoft.com/.default"]

    result = SourceMicrosoftSharePointClient._get_scope()

    assert result == expected_scope


def test_client_property_raises_error_when_config_missing():
    """Test that client property raises ValueError when config attribute is missing after initialization."""
    with patch("source_microsoft_sharepoint.sharepoint_client.ConfidentialClientApplication"):
        client = SourceMicrosoftSharePointClient(create_mock_config())
        client.config = None

        with pytest.raises(ValueError, match="Configuration is missing; cannot create the Office365 graph client."):
            _ = client.client
