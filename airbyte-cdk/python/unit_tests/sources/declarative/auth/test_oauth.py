#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import freezegun
import pendulum
import pytest
import requests
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
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

    def test_refresh_without_refresh_token(self):
        """
        Should work fine for grant_type client_credentials.
        """
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] }}",
            client_secret="{{ config['client_secret'] }}",
            config=config,
            parameters={},
            grant_type="client_credentials",
        )
        body = oauth.build_refresh_request_body()
        expected = {
            "grant_type": "client_credentials",
            "client_id": "some_client_id",
            "client_secret": "some_client_secret",
            "refresh_token": None,
            "scopes": None,
        }
        assert body == expected

    def test_error_on_refresh_token_grant_without_refresh_token(self):
        """
        Should throw an error if grant_type refresh_token is configured without refresh_token.
        """
        with pytest.raises(ValueError):
            DeclarativeOauth2Authenticator(
                token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
                client_id="{{ config['client_id'] }}",
                client_secret="{{ config['client_secret'] }}",
                config=config,
                parameters={},
                grant_type="refresh_token",
            )

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
            ("2020-01-02T00:00:00Z", "YYYY-MM-DDTHH:mm:ss[Z]"),
            ("2020-01-02T00:00:00.000000+00:00", "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"),
            ("2020-01-02", "YYYY-MM-DD"),
        ],
        ids=["rfc3339", "iso8601", "simple_date"],
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

    @pytest.mark.parametrize(
        "expires_in_response, next_day, raises",
        [
            (86400, "2020-01-02T00:00:00Z", False),
            (86400.1, "2020-01-02T00:00:00Z", False),
            ("86400", "2020-01-02T00:00:00Z", False),
            ("86400.1", "2020-01-02T00:00:00Z", False),
            ("2020-01-02T00:00:00Z", "2020-01-02T00:00:00Z", True),
        ],
        ids=["time_in_seconds", "time_in_seconds_float", "time_in_seconds_str", "time_in_seconds_str_float", "invalid"],
    )
    @freezegun.freeze_time("2020-01-01")
    def test_set_token_expiry_date_no_format(self, mocker, expires_in_response, next_day, raises):
        config.update({"token_expiry_date": pendulum.parse(next_day).subtract(days=2).to_rfc3339_string()})
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] }}",
            client_secret="{{ config['client_secret'] }}",
            refresh_token="{{ config['refresh_token'] }}",
            config=config,
            scopes=["scope1", "scope2"],
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
        if raises:
            with pytest.raises(ValueError):
                oauth.get_access_token()
        else:
            token = oauth.get_access_token()
            assert "access_token" == token
            assert oauth.get_token_expiry_date() == pendulum.parse(next_day)


def mock_request(method, url, data, headers):
    if url == "refresh_end" and headers == {"Content-Type": "application/json"}:
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}, {headers}")
