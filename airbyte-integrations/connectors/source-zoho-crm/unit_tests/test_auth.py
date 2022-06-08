#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

from source_zoho_crm.auth import ZohoOauth2Authenticator

authenticator = ZohoOauth2Authenticator("http://dummy.url/oauth/v2/token", "client_id", "client_secret", "refresh_token")


def test_refresh_access_token(mocker, request_mocker):
    request = request_mocker(content=b'{"access_token": "access_token", "expires_in": 86400}')
    mocker.patch("source_zoho_crm.auth.requests.request", request)

    token, expires = authenticator.refresh_access_token()
    assert (token, expires) == ("access_token", 24 * 60 * 60)
    request.assert_called_once_with(
        method="POST",
        url="http://dummy.url/oauth/v2/token",
        params={
            "refresh_token": "refresh_token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "grant_type": "refresh_token",
        },
    )


def test_get_auth_header(mocker):
    mocker.patch.object(ZohoOauth2Authenticator, "get_access_token", Mock(return_value="token"))
    assert authenticator.get_auth_header() == {"Authorization": "Zoho-oauthtoken token"}
