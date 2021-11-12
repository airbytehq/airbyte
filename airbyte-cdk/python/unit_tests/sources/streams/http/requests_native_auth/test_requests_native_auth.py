#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import logging

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import MultipleTokenAuthenticator, Oauth2Authenticator, TokenAuthenticator
from requests import Response

LOGGER = logging.getLogger(__name__)


def test_token_authenticator():
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = TokenAuthenticator(token="test-token")
    header1 = token_auth.get_auth_header()
    header2 = token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    token_auth(prepared_request)

    assert {"Authorization": "Bearer test-token"} == prepared_request.headers
    assert {"Authorization": "Bearer test-token"} == header1
    assert {"Authorization": "Bearer test-token"} == header2


def test_multiple_token_authenticator():
    multiple_token_auth = MultipleTokenAuthenticator(tokens=["token1", "token2"])
    header1 = multiple_token_auth.get_auth_header()
    header2 = multiple_token_auth.get_auth_header()
    header3 = multiple_token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    multiple_token_auth(prepared_request)

    assert {"Authorization": "Bearer token2"} == prepared_request.headers
    assert {"Authorization": "Bearer token1"} == header1
    assert {"Authorization": "Bearer token2"} == header2
    assert {"Authorization": "Bearer token1"} == header3


class TestOauth2Authenticator:
    """
    Test class for OAuth2Authenticator.
    """

    refresh_endpoint = "refresh_end"
    client_id = "client_id"
    client_secret = "client_secret"
    refresh_token = "refresh_token"

    def test_get_auth_header_fresh(self, mocker):
        """
        Should not retrieve new token if current token is valid.
        """
        oauth = Oauth2Authenticator(
            token_refresh_endpoint=TestOauth2Authenticator.refresh_endpoint,
            client_id=TestOauth2Authenticator.client_id,
            client_secret=TestOauth2Authenticator.client_secret,
            refresh_token=TestOauth2Authenticator.refresh_token,
        )

        mocker.patch.object(Oauth2Authenticator, "refresh_access_token", return_value=("access_token", 1000))
        header = oauth.get_auth_header()
        assert {"Authorization": "Bearer access_token"} == header

    def test_get_auth_header_expired(self, mocker):
        """
        Should retrieve new token if current token is expired.
        """
        oauth = Oauth2Authenticator(
            token_refresh_endpoint=TestOauth2Authenticator.refresh_endpoint,
            client_id=TestOauth2Authenticator.client_id,
            client_secret=TestOauth2Authenticator.client_secret,
            refresh_token=TestOauth2Authenticator.refresh_token,
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
            token_refresh_endpoint=TestOauth2Authenticator.refresh_endpoint,
            client_id=TestOauth2Authenticator.client_id,
            client_secret=TestOauth2Authenticator.client_secret,
            refresh_token=TestOauth2Authenticator.refresh_token,
            scopes=scopes,
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

    def test_refresh_access_token(self, mocker):
        oauth = Oauth2Authenticator(
            token_refresh_endpoint=TestOauth2Authenticator.refresh_endpoint,
            client_id=TestOauth2Authenticator.client_id,
            client_secret=TestOauth2Authenticator.client_secret,
            refresh_token=TestOauth2Authenticator.refresh_token,
        )
        resp = Response()
        resp.status_code = 200

        mocker.patch.object(requests, "request", return_value=resp)
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": 1000})
        token = oauth.refresh_access_token()

        assert ("access_token", 1000) == token

    def test_auth_call_method(self, mocker):
        oauth = Oauth2Authenticator(
            token_refresh_endpoint=TestOauth2Authenticator.refresh_endpoint,
            client_id=TestOauth2Authenticator.client_id,
            client_secret=TestOauth2Authenticator.client_secret,
            refresh_token=TestOauth2Authenticator.refresh_token,
        )

        mocker.patch.object(Oauth2Authenticator, "refresh_access_token", return_value=("access_token", 1000))
        prepared_request = requests.PreparedRequest()
        prepared_request.headers = {}
        oauth(prepared_request)

        assert {"Authorization": "Bearer access_token"} == prepared_request.headers
