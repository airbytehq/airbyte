#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from unittest.mock import Mock

import freezegun
import pendulum
import pytest
import requests
from airbyte_cdk.models import OrchestratorType, Type
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
        token, expires_in = oauth.refresh_access_token()

        assert isinstance(expires_in, int)
        assert ("access_token", 1000) == (token, expires_in)

        # Test with expires_in as str
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": "2000"})
        token, expires_in = oauth.refresh_access_token()

        assert isinstance(expires_in, int)
        assert ("access_token", 2000) == (token, expires_in)

    @pytest.mark.parametrize("error_code", (429, 500, 502, 504))
    def test_refresh_access_token_retry(self, error_code, requests_mock):
        oauth = Oauth2Authenticator(
            f"https://{TestOauth2Authenticator.refresh_endpoint}",
            TestOauth2Authenticator.client_id,
            TestOauth2Authenticator.client_secret,
            TestOauth2Authenticator.refresh_token
        )
        requests_mock.post(
            f"https://{TestOauth2Authenticator.refresh_endpoint}",
            [
                {"status_code": error_code}, {"status_code": error_code}, {"json": {"access_token": "token", "expires_in": 10}}
            ]
        )
        token, expires_in = oauth.refresh_access_token()
        assert isinstance(expires_in, int)
        assert (token, expires_in) == ("token", 10)
        assert requests_mock.call_count == 3

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
                "token_expiry_date": "2022-12-31T00:00:00+00:00"
            }
        }

    @pytest.fixture
    def invalid_connector_config(self):
        return {"no_credentials_key": "foo"}

    def test_init(self, connector_config):
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            client_id=connector_config["credentials"]["client_id"],
            client_secret=connector_config["credentials"]["client_secret"],
        )
        assert authenticator.access_token == connector_config["credentials"]["access_token"]
        assert authenticator.get_refresh_token() == connector_config["credentials"]["refresh_token"]
        assert authenticator.get_token_expiry_date() == pendulum.parse(connector_config["credentials"]["token_expiry_date"])

    @freezegun.freeze_time("2022-12-31")
    @pytest.mark.parametrize(
        "test_name, expires_in_value, expiry_date_format, expected_expiry_date",
        [
            ("number_of_seconds", 42, None, "2022-12-31T00:00:42+00:00"),
            ("string_of_seconds", "42", None, "2022-12-31T00:00:42+00:00"),
            ("date_format", "2023-04-04", "YYYY-MM-DD", "2023-04-04T00:00:00+00:00"),
        ]
    )
    def test_given_no_message_repository_get_access_token(self, test_name, expires_in_value, expiry_date_format, expected_expiry_date, capsys, mocker, connector_config):
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            client_id=connector_config["credentials"]["client_id"],
            client_secret=connector_config["credentials"]["client_secret"],
            token_expiry_date_format=expiry_date_format,
        )
        authenticator.refresh_access_token = mocker.Mock(return_value=("new_access_token", expires_in_value, "new_refresh_token"))
        authenticator.token_has_expired = mocker.Mock(return_value=True)
        access_token = authenticator.get_access_token()
        captured = capsys.readouterr()
        airbyte_message = json.loads(captured.out)
        expected_new_config = connector_config.copy()
        expected_new_config["credentials"]["access_token"] = "new_access_token"
        expected_new_config["credentials"]["refresh_token"] = "new_refresh_token"
        expected_new_config["credentials"]["token_expiry_date"] = expected_expiry_date
        assert airbyte_message["control"]["connectorConfig"]["config"] == expected_new_config
        assert authenticator.access_token == access_token == "new_access_token"
        assert authenticator.get_refresh_token() == "new_refresh_token"
        assert authenticator.get_token_expiry_date() > pendulum.now()
        authenticator.token_has_expired = mocker.Mock(return_value=False)
        access_token = authenticator.get_access_token()
        captured = capsys.readouterr()
        assert not captured.out
        assert authenticator.access_token == access_token == "new_access_token"

    def test_given_message_repository_when_get_access_token_emit_message(self, mocker, connector_config):
        message_repository = Mock()
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            client_id=connector_config["credentials"]["client_id"],
            client_secret=connector_config["credentials"]["client_secret"],
            token_expiry_date_format="YYYY-MM-DD",
            message_repository=message_repository,
        )
        authenticator.refresh_access_token = mocker.Mock(return_value=("new_access_token", "2023-04-04", "new_refresh_token"))
        authenticator.token_has_expired = mocker.Mock(return_value=True)

        authenticator.get_access_token()

        emitted_message = message_repository.emit_message.call_args_list[0].args[0]
        assert emitted_message.type == Type.CONTROL
        assert emitted_message.control.type == OrchestratorType.CONNECTOR_CONFIG
        assert emitted_message.control.connectorConfig.config["credentials"]["access_token"] == "new_access_token"
        assert emitted_message.control.connectorConfig.config["credentials"]["refresh_token"] == "new_refresh_token"
        assert emitted_message.control.connectorConfig.config["credentials"]["token_expiry_date"] == "2023-04-04T00:00:00+00:00"
        assert emitted_message.control.connectorConfig.config["credentials"]["client_id"] == "my_client_id"
        assert emitted_message.control.connectorConfig.config["credentials"]["client_secret"] == "my_client_secret"

    def test_refresh_access_token(self, mocker, connector_config):
        authenticator = SingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            client_id=connector_config["credentials"]["client_id"],
            client_secret=connector_config["credentials"]["client_secret"],
        )

        authenticator._get_refresh_access_token_response = mocker.Mock(
            return_value={
                authenticator.get_access_token_name(): "new_access_token",
                authenticator.get_expires_in_name(): "42",
                authenticator.get_refresh_token_name(): "new_refresh_token",
            }
        )
        assert authenticator.refresh_access_token() == ("new_access_token", "42", "new_refresh_token")


def mock_request(method, url, data, headers):
    if url == "refresh_end" and headers == {"Content-Type": "application/json"}:
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}, {headers}")
