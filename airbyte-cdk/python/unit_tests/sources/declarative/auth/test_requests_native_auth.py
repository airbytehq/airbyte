#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import pendulum
import pytest
import requests
from airbyte_cdk.sources.declarative.auth.oauth import Oauth2Authenticator
from requests import Response

LOGGER = logging.getLogger(__name__)

resp = Response()

config = {
    "refresh_endpoint": "refresh_end",
    "client_id": "some_client_id",
    "client_secret": "some_client_secret",
    "refresh_token": "some_refresh_token",
    "token_expiry_date": pendulum.now().subtract(days=2).to_rfc3339_string(),
    "custom_field": "in_outbound_request",
    "another_field": "exists_in_body",
}


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

    @pytest.mark.parametrize(
        "test_name, use_interpolated", [("test_using_concrete_values", False), ("test_using_interpolated_values", True)]
    )
    def test_refresh_request_body(self, test_name, use_interpolated):
        """
        Request body should match given configuration.
        """
        scopes = ["scope1", "scope2"]
        oauth = self.get_authenticator(use_interpolated)
        body = oauth.get_refresh_request_body()
        expected = {
            "grant_type": "refresh_token",
            "client_id": "some_client_id",
            "client_secret": "some_client_secret",
            "refresh_token": "some_refresh_token",
            "scopes": scopes,
            "custom_field": "in_outbound_request",
            "another_field": "exists_in_body",
        }
        assert body == expected

    @pytest.mark.parametrize(
        "test_name, use_interpolated", [("test_using_concrete_values", False), ("test_using_interpolated_values", True)]
    )
    def test_refresh_access_token(self, mocker, test_name, use_interpolated):
        oauth = self.get_authenticator(use_interpolated)

        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": 1000})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
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

    @staticmethod
    def get_authenticator(use_interpolated: bool):
        if use_interpolated:
            return Oauth2Authenticator(
                token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
                client_id="{{ config['client_id'] }}",
                client_secret="{{ config['client_secret'] }}",
                refresh_token="{{ config['refresh_token'] }}",
                config=config,
                scopes=["scope1", "scope2"],
                token_expiry_date="{{ config['token_expiry_date'] }}",
                refresh_request_body={
                    "custom_field": "{{ config['custom_field'] }}",
                    "another_field": "{{ config['another_field'] }}",
                    "scopes": ["no_override"],
                },
            )
        return Oauth2Authenticator(
            token_refresh_endpoint="refresh_end",
            client_id="some_client_id",
            client_secret="some_client_secret",
            refresh_token="some_refresh_token",
            config=config,
            scopes=["scope1", "scope2"],
            token_expiry_date=pendulum.now().add(days=3).to_rfc3339_string(),
            refresh_request_body={"custom_field": "in_outbound_request", "another_field": "exists_in_body", "scopes": ["no_override"]},
        )


def mock_refresh_access_token(self):
    if self.refresh_token.eval(self.config) == "some_refresh_token":
        return "access_token", 1000
    return "", 0


def mock_request(method, url, data):
    if url == "refresh_end":
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}")
