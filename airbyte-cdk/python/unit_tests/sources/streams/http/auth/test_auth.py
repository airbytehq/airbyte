#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

import pytest
from airbyte_cdk.sources.streams.http.auth import (
    BasicHttpAuthenticator,
    MultipleTokenAuthenticator,
    NoAuth,
    Oauth2Authenticator,
    TokenAuthenticator,
)

LOGGER = logging.getLogger(__name__)


def test_token_authenticator():
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token = TokenAuthenticator("test-token")
    header = token.get_auth_header()
    assert {"Authorization": "Bearer test-token"} == header
    header = token.get_auth_header()
    assert {"Authorization": "Bearer test-token"} == header


def test_multiple_token_authenticator():
    token = MultipleTokenAuthenticator(["token1", "token2"])
    header1 = token.get_auth_header()
    assert {"Authorization": "Bearer token1"} == header1
    header2 = token.get_auth_header()
    assert {"Authorization": "Bearer token2"} == header2
    header3 = token.get_auth_header()
    assert {"Authorization": "Bearer token1"} == header3


def test_no_auth():
    """
    Should always return empty body, no matter how many times token is retrieved.
    """
    no_auth = NoAuth()
    assert {} == no_auth.get_auth_header()
    no_auth = NoAuth()
    assert {} == no_auth.get_auth_header()


def test_basic_authenticator():
    token = BasicHttpAuthenticator("client_id", "client_secret")
    header = token.get_auth_header()
    assert {"Authorization": "Basic Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ="} == header


class TestOauth2Authenticator:
    """
    Test class for OAuth2Authenticator.
    """

    refresh_endpoint = "https://some_url.com/v1"
    client_id = "client_id"
    client_secret = "client_secret"
    refresh_token = "refresh_token"
    refresh_access_token_headers = {"Header_1": "value 1", "Header_2": "value 2"}
    refresh_access_token_authenticator = BasicHttpAuthenticator(client_id, client_secret)

    def test_get_auth_header_fresh(self, mocker):
        """
        Should not retrieve new token if current token is valid.
        """
        oauth = Oauth2Authenticator(
            TestOauth2Authenticator.refresh_endpoint,
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token,
        )

        mocker.patch.object(Oauth2Authenticator, "refresh_access_token", return_value=("access_token", 1000))
        header = oauth.get_auth_header()
        assert {"Authorization": "Bearer access_token"} == header

    def test_get_auth_header_expired(self, mocker):
        """
        Should retrieve new token if current token is expired.
        """
        oauth = Oauth2Authenticator(
            TestOauth2Authenticator.refresh_endpoint,
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token,
        )

        expire_immediately = 0
        mocker.patch.object(Oauth2Authenticator, "refresh_access_token", return_value=("access_token_1", expire_immediately))
        oauth.get_auth_header()  # Set the first expired token.

        valid_100_secs = 100
        mocker.patch.object(Oauth2Authenticator, "refresh_access_token", return_value=("access_token_2", valid_100_secs))
        header = oauth.get_auth_header()
        assert {"Authorization": "Bearer access_token_2"} == header

    def test_refresh_request_body(self):
        """
        Request body should match given configuration.
        """
        scopes = ["scope1", "scope2"]
        oauth = Oauth2Authenticator(
            TestOauth2Authenticator.refresh_endpoint,
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token,
            scopes,
        )
        body = oauth.get_refresh_request_body()
        expected = {
            "grant_type": "refresh_token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
            "scopes": scopes,
        }
        assert body == expected

    def test_refresh_access_token(self, requests_mock):
        mock_refresh_token_call = requests_mock.post(
            TestOauth2Authenticator.refresh_endpoint, json={"access_token": "token", "expires_in": 10}
        )

        oauth = Oauth2Authenticator(
            TestOauth2Authenticator.refresh_endpoint,
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token,
            refresh_access_token_headers=TestOauth2Authenticator.refresh_access_token_headers,
        )

        token, expires_in = oauth.refresh_access_token()

        assert isinstance(expires_in, int)
        assert ("token", 10) == (token, expires_in)
        for header in self.refresh_access_token_headers:
            assert header in mock_refresh_token_call.last_request.headers
            assert self.refresh_access_token_headers[header] == mock_refresh_token_call.last_request.headers[header]
        assert mock_refresh_token_call.called

    @pytest.mark.parametrize("error_code", (429, 500, 502, 504))
    def test_refresh_access_token_retry(self, error_code, requests_mock):
        oauth = Oauth2Authenticator(
            TestOauth2Authenticator.refresh_endpoint,
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token,
        )
        requests_mock.post(
            TestOauth2Authenticator.refresh_endpoint,
            [{"status_code": error_code}, {"status_code": error_code}, {"json": {"access_token": "token", "expires_in": 10}}],
        )
        token, expires_in = oauth.refresh_access_token()
        assert (token, expires_in) == ("token", 10)
        assert requests_mock.call_count == 3

    def test_refresh_access_authenticator(self):
        oauth = Oauth2Authenticator(
            TestOauth2Authenticator.refresh_endpoint,
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token,
            refresh_access_token_authenticator=TestOauth2Authenticator.refresh_access_token_authenticator,
        )
        expected_headers = {"Authorization": "Basic Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ="}
        assert expected_headers == oauth.get_refresh_access_token_headers()
