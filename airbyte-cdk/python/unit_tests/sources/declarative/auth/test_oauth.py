#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

import freezegun
import pendulum
import pytest
import requests
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator, DeclarativeSingleUseRefreshTokenOauth2Authenticator
from requests import Response

LOGGER = logging.getLogger(__name__)

resp = Response()

config = {
    "refresh_endpoint": "refresh_end",
    "client_id": "some_client_id",
    "client_secret": "some_client_secret",
    "token_expiry_date": pendulum.now().subtract(days=2).to_rfc3339_string(),
    "custom_field": "in_outbound_request",
    "another_field": "exists_in_body",
    "grant_type": "some_grant_type",
}
parameters = {"refresh_token": "some_refresh_token"}


def mock_request(method, url, data):
    if url == "refresh_end":
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}")


class TestOauth2Authenticator:
    """
    Test class for OAuth2Authenticator.
    """

    def test_refresh_request_body(self):
        """
        Request body should match given configuration.
        """
        scopes = ["scope1", "scope2"]
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] }}",
            client_secret="{{ config['client_secret'] }}",
            refresh_token="{{ parameters['refresh_token'] }}",
            config=config,
            scopes=["scope1", "scope2"],
            token_expiry_date="{{ config['token_expiry_date'] }}",
            refresh_request_body={
                "custom_field": "{{ config['custom_field'] }}",
                "another_field": "{{ config['another_field'] }}",
                "scopes": ["no_override"],
            },
            parameters=parameters,
            grant_type="{{ config['grant_type'] }}",
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
        oauth = DeclarativeOauth2Authenticator(
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
            parameters={},
        )

        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": 1000})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        token = oauth.refresh_access_token()

        assert ("access_token", 1000) == token

    @pytest.mark.parametrize(
        "expires_in_response, token_expiry_date_format",
        [
            (86400, None),
            ("2020-01-02T00:00:00Z", "YYYY-MM-DDTHH:mm:ss[Z]"),
            ("2020-01-02T00:00:00.000000+00:00", "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"),
            ("2020-01-02", "YYYY-MM-DD"),
        ],
        ids=["time_in_seconds", "rfc3339", "iso8601", "simple_date"],
    )
    @freezegun.freeze_time("2020-01-01")
    def test_refresh_access_token_expire_format(self, mocker, expires_in_response, token_expiry_date_format):
        next_day = "2020-01-02T00:00:00Z"
        config.update({"token_expiry_date": pendulum.parse(next_day).subtract(days=2).to_rfc3339_string()})
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] }}",
            client_secret="{{ config['client_secret'] }}",
            refresh_token="{{ config['refresh_token'] }}",
            config=config,
            scopes=["scope1", "scope2"],
            token_expiry_date="{{ config['token_expiry_date'] }}",
            token_expiry_date_format=token_expiry_date_format,
            refresh_request_body={
                "custom_field": "{{ config['custom_field'] }}",
                "another_field": "{{ config['another_field'] }}",
                "scopes": ["no_override"],
            },
            parameters={},
        )

        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": expires_in_response})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        token = oauth.get_access_token()
        assert "access_token" == token
        assert oauth.get_token_expiry_date() == pendulum.parse(next_day)


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
        authenticator = DeclarativeSingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            parameters={}
        )
        assert authenticator.access_token == connector_config["credentials"]["access_token"]
        assert authenticator.get_refresh_token() == connector_config["credentials"]["refresh_token"]
        assert authenticator.get_token_expiry_date() == pendulum.parse(connector_config["credentials"]["token_expiry_date"])

    def test_init_with_invalid_config(self, invalid_connector_config):
        with pytest.raises(ValueError):
            DeclarativeSingleUseRefreshTokenOauth2Authenticator(
                invalid_connector_config,
                token_refresh_endpoint="foobar",
                parameters={}
            )

    @freezegun.freeze_time("2022-12-31")
    @pytest.mark.parametrize("expires_in", (42, "42", "2022-12-31T00:00:42+00:00"))
    def test_get_access_token(self, capsys, mocker, connector_config, expires_in):
        authenticator = DeclarativeSingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            parameters={}
        )
        authenticator.refresh_access_token = mocker.Mock(return_value=("new_access_token", expires_in, "new_refresh_token"))
        authenticator.token_has_expired = mocker.Mock(return_value=True)
        access_token = authenticator.get_access_token()
        captured = capsys.readouterr()
        airbyte_message = json.loads(captured.out)
        expected_new_config = connector_config.copy()
        expected_new_config["credentials"]["access_token"] = "new_access_token"
        expected_new_config["credentials"]["refresh_token"] = "new_refresh_token"
        expected_new_config["credentials"]["token_expiry_date"] = "2022-12-31T00:00:42+00:00"
        assert airbyte_message["control"]["connectorConfig"]["config"] == expected_new_config
        assert authenticator.access_token == access_token == "new_access_token"
        assert authenticator.get_refresh_token() == "new_refresh_token"
        assert authenticator.get_token_expiry_date() > pendulum.now()
        authenticator.token_has_expired = mocker.Mock(return_value=False)
        access_token = authenticator.get_access_token()
        captured = capsys.readouterr()
        assert not captured.out
        assert authenticator.access_token == access_token == "new_access_token"

    @pytest.mark.parametrize("expires_in", (42, "42", "2022-12-31T00:00:42+00:00"))
    def test_refresh_access_token(self, mocker, connector_config, expires_in):
        authenticator = DeclarativeSingleUseRefreshTokenOauth2Authenticator(
            connector_config,
            token_refresh_endpoint="foobar",
            parameters={}
        )

        authenticator._get_refresh_access_token_response = mocker.Mock(
            return_value={
                authenticator.get_access_token_name(): "new_access_token",
                authenticator.get_expires_in_name(): expires_in,
                authenticator.get_refresh_token_name(): "new_refresh_token",
            }
        )
        assert authenticator.refresh_access_token() == ("new_access_token", expires_in, "new_refresh_token")
