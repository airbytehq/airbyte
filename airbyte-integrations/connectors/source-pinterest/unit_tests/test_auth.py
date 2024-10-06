#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging

import pendulum
import pytest
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from requests import Response
from source_pinterest.python_stream_auth import PinterestOauthAuthenticator

LOGGER = logging.getLogger(__name__)

resp = Response()

class TestPinterestOauthAuthenticator:
    """
    Test class for custom PinterestOauthAuthenticator, derived from the CDK's Oauth2Authenticator class.
    """

    refresh_endpoint = "refresh_end"
    client_id = "client_id"
    client_secret = "client_secret"
    refresh_token = "refresh_token"

    @pytest.fixture
    def oauth(self):
        return PinterestOauthAuthenticator(
            token_refresh_endpoint=self.refresh_endpoint,
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
            scopes=["scope1", "scope2"],
            token_expiry_date=pendulum.now().add(days=3),
            refresh_request_body={"custom_field": "in_outbound_request", "another_field": "exists_in_body", "scopes": ["no_override"]},
        )

    def test_refresh_access_token_success(self, mocker, oauth):
        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": 1000})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        token, expires_in = oauth.refresh_access_token()

        assert isinstance(expires_in, int)
        assert ("access_token", 1000) == (token, expires_in)

    def test_refresh_access_token_missing_token(self, mocker, oauth):
        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"expires_in": 1000})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)

        with pytest.raises(Exception, match="Token refresh API response was missing access token access_token"):
            oauth.refresh_access_token()

    def test_refresh_access_token_http_error(self, mocker, oauth):
        resp.status_code = 400
        mocker.patch.object(resp, "json", return_value={"error": "invalid_request"})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)

        with pytest.raises(requests.exceptions.HTTPError):
            oauth.refresh_access_token()

    def test_refresh_access_token_invalid_or_expired(self, mocker, oauth):
        mocker.patch.object(requests, "request", side_effect=requests.exceptions.RequestException("Request failed", response=resp))
        mocker.patch.object(resp, "status_code", 400)
        mocker.patch.object(oauth, "_wrap_refresh_token_exception", return_value=True)

        with pytest.raises(AirbyteTracedException, match="Refresh token is invalid or expired. Please re-authenticate from Sources/<your source>/Settings."):
            oauth.refresh_access_token()


def mock_request(method, url, data, headers):
    if url == "refresh_end":
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}, {headers}")
