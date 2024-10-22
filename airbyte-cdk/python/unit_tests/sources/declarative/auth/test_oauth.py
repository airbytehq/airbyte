#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base64
import logging
from unittest.mock import Mock

import freezegun
import pendulum
import pytest
import requests
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
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

    def test_refresh_with_encode_config_params(self):
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] | base64encode }}",
            client_secret="{{ config['client_secret'] | base64encode }}",
            config=config,
            parameters={},
            grant_type="client_credentials",
        )
        body = oauth.build_refresh_request_body()
        expected = {
            "grant_type": "client_credentials",
            "client_id": base64.b64encode(config["client_id"].encode("utf-8")).decode(),
            "client_secret": base64.b64encode(config["client_secret"].encode("utf-8")).decode(),
            "refresh_token": None,
        }
        assert body == expected

    def test_refresh_with_decode_config_params(self):
        updated_config_fields = {
            "client_id": base64.b64encode(config["client_id"].encode("utf-8")).decode(),
            "client_secret": base64.b64encode(config["client_secret"].encode("utf-8")).decode(),
        }
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] | base64decode }}",
            client_secret="{{ config['client_secret'] | base64decode }}",
            config=config | updated_config_fields,
            parameters={},
            grant_type="client_credentials",
        )
        body = oauth.build_refresh_request_body()
        expected = {
            "grant_type": "client_credentials",
            "client_id": "some_client_id",
            "client_secret": "some_client_secret",
            "refresh_token": None,
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

        filtered = filter_secrets("access_token")
        assert filtered == "****"

    def test_refresh_access_token_missing_access_token(self, mocker):
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
        mocker.patch.object(resp, "json", return_value={"expires_in": 1000})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        with pytest.raises(Exception):
            oauth.refresh_access_token()

    @pytest.mark.parametrize(
        "timestamp, expected_date",
        [
            (1640995200, "2022-01-01T00:00:00Z"),
            ("1650758400", "2022-04-24T00:00:00Z"),
        ],
        ids=["timestamp_as_integer", "timestamp_as_integer_inside_string"],
    )
    def test_initialize_declarative_oauth_with_token_expiry_date_as_timestamp(self, timestamp, expected_date):
        # TODO: should be fixed inside DeclarativeOauth2Authenticator, remove next line after fixing
        with pytest.raises(TypeError):
            oauth = DeclarativeOauth2Authenticator(
                token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
                client_id="{{ config['client_id'] }}",
                client_secret="{{ config['client_secret'] }}",
                refresh_token="{{ parameters['refresh_token'] }}",
                config=config | {"token_expiry_date": timestamp},
                scopes=["scope1", "scope2"],
                token_expiry_date="{{ config['token_expiry_date'] }}",
                refresh_request_body={
                    "custom_field": "{{ config['custom_field'] }}",
                    "another_field": "{{ config['another_field'] }}",
                    "scopes": ["no_override"],
                },
                parameters={},
            )

            assert oauth.get_token_expiry_date() == pendulum.parse(expected_date)

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
        message_repository = Mock()
        oauth = DeclarativeOauth2Authenticator(
            token_refresh_endpoint="{{ config['refresh_endpoint'] }}",
            client_id="{{ config['client_id'] }}",
            client_secret="{{ config['client_secret'] }}",
            refresh_token="{{ config['refresh_token'] }}",
            config=config,
            scopes=["scope1", "scope2"],
            token_expiry_date="{{ config['token_expiry_date'] }}",
            token_expiry_date_format=token_expiry_date_format,
            token_expiry_is_time_of_expiration=True,
            refresh_request_body={
                "custom_field": "{{ config['custom_field'] }}",
                "another_field": "{{ config['another_field'] }}",
                "scopes": ["no_override"],
            },
            message_repository=message_repository,
            parameters={},
        )

        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": expires_in_response})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        token = oauth.get_access_token()
        assert "access_token" == token
        assert oauth.get_token_expiry_date() == pendulum.parse(next_day)
        assert message_repository.log_message.call_count == 1

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

    def test_error_handling(self, mocker):
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
        resp.status_code = 400
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": 123})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        with pytest.raises(requests.exceptions.HTTPError) as e:
            oauth.refresh_access_token()
            assert e.value.errno == 400


def mock_request(method, url, data):
    if url == "refresh_end":
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}")
