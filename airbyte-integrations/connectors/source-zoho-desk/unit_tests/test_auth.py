# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch
from source_zoho_desk.auth import ZohoOauth2Authenticator

authenticator = ZohoOauth2Authenticator("http://dummy.url/oauth/v2/token", "client_id", "client_secret", "refresh_token")


@patch("requests.request")
def test_refresh_access_token(mock_request):
    mock_response = Mock()
    mock_response.json.return_value = {"access_token": "access_token", "expires_in": 86400}
    mock_request.return_value = mock_response

    token, expires = authenticator.refresh_access_token()
    assert (token, expires) == ("access_token", 86400)
    mock_request.assert_called_once_with(
        method="POST",
        url="http://dummy.url/oauth/v2/token",
        params={
            "refresh_token": "refresh_token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "grant_type": "refresh_token",
        },
    )


@patch.object(ZohoOauth2Authenticator, "get_access_token")
def test_get_auth_header(mock_get_access_token):
    mock_get_access_token.return_value = "token"
    assert authenticator.get_auth_header() == {"Authorization": "Zoho-oauthtoken token"}