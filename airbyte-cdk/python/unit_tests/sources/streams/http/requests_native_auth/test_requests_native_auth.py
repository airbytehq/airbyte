#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pendulum
import pytest
import requests
from airbyte_cdk.config_observation import ObservedDict
from airbyte_cdk.sources.streams.http.requests_native_auth import (
    BasicHttpAuthenticator,
    MultipleTokenAuthenticator,
    Oauth2Authenticator,
    SingleUseRefreshTokenOauth2Authenticator,
    TokenAuthenticator,
)
from requests import Response

LOGGER = logging.getLogger(__name__)

resp = Response()


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


def test_basic_http_authenticator():
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = BasicHttpAuthenticator(username="user", password="password")
    header1 = token_auth.get_auth_header()
    header2 = token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    token_auth(prepared_request)

    assert {"Authorization": "Basic dXNlcjpwYXNzd29yZA=="} == prepared_request.headers
    assert {"Authorization": "Basic dXNlcjpwYXNzd29yZA=="} == header1
    assert {"Authorization": "Basic dXNlcjpwYXNzd29yZA=="} == header2


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
            token_refresh_endpoint="refresh_end",
            client_id="some_client_id",
            client_secret="some_client_secret",
            refresh_token="some_refresh_token",
            scopes=["scope1", "scope2"],
            token_expiry_date=pendulum.now().add(days=3),
            grant_type="some_grant_type",
            refresh_request_body={"custom_field": "in_outbound_request", "another_field": "exists_in_body", "scopes": ["no_override"]},
        )
        body = oauth.build_refresh_request_body()
        expected = {
            "grant_type": "some_grant_type",
            "client_id": "some_client_id",
            "client_secret": "some_client_secret",
            "refresh_token": "some_refresh_token",
            "scopes": scopes,
            "custom_field": "in_outbound_request",
            "another_field": "exists_in_body",
        }
        assert body == expected

    def test_refresh_access_token(self, mocker):
        oauth = Oauth2Authenticator(
            token_refresh_endpoint="refresh_end",
            client_id="some_client_id",
            client_secret="some_client_secret",
            refresh_token="some_refresh_token",
            scopes=["scope1", "scope2"],
            token_expiry_date=pendulum.now().add(days=3),
            refresh_request_body={"custom_field": "in_outbound_request", "another_field": "exists_in_body", "scopes": ["no_override"]},
        )

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


class TestSingleUseRefreshTokenOauth2Authenticator:
    @pytest.fixture
    def connector_config(self):
        return {
            "credentials": {
                "access_token": "my_access_token",
                "refresh_token": "my_refresh_token",
                "client_id": "my_client_id",
                "client_secret": "my_client_secret",
            }
        }

    @pytest.fixture
    def invalid_connector_config(self):
        return {"no_credentials_key": "foo"}

    def test_init(self, connector_config):
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
        )
        assert isinstance(authenticator._connector_config, ObservedDict)

    def test_init_with_invalid_config(self, invalid_connector_config):
        with pytest.raises(ValueError):
            SingleUseRefreshTokenOauth2Authenticator(
                invalid_connector_config,
                token_refresh_endpoint="foobar",
            )

    def test_get_access_token(self, capsys, mocker, connector_config):
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
        )
        authenticator.refresh_access_token = mocker.Mock(return_value=("new_access_token", 42, "new_refresh_token"))
        authenticator.token_has_expired = mocker.Mock(return_value=True)
        access_token = authenticator.get_access_token()
        captured = capsys.readouterr()
        airbyte_message = json.loads(captured.out)
        expected_new_config = connector_config.copy()
        expected_new_config["credentials"]["refresh_token"] = "new_refresh_token"
        assert airbyte_message["control"]["connectorConfig"]["config"] == expected_new_config
        assert authenticator.access_token == access_token == "new_access_token"
        assert authenticator.get_refresh_token() == "new_refresh_token"
        assert authenticator.get_token_expiry_date() > pendulum.now()
        authenticator.token_has_expired = mocker.Mock(return_value=False)
        access_token = authenticator.get_access_token()
        captured = capsys.readouterr()
        assert not captured.out
        assert authenticator.access_token == access_token == "new_access_token"

    def test_refresh_access_token(self, mocker, connector_config):
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
        )
        authenticator._get_refresh_access_token_response = mocker.Mock(
            return_value={
                authenticator.get_access_token_name(): "new_access_token",
                authenticator.get_expires_in_name(): 42,
                authenticator.get_refresh_token_name(): "new_refresh_token",
            }
        )
        assert authenticator.refresh_access_token() == ("new_access_token", 42, "new_refresh_token")


def mock_request(method, url, data):
    if url == "refresh_end":
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}")
