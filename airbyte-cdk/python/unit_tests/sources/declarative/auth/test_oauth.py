#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import pendulum
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
options = {"refresh_token": "some_refresh_token"}


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
            refresh_token="{{ options['refresh_token'] }}",
            config=config,
            scopes=["scope1", "scope2"],
            token_expiry_date="{{ config['token_expiry_date'] }}",
            refresh_request_body={
                "custom_field": "{{ config['custom_field'] }}",
                "another_field": "{{ config['another_field'] }}",
                "scopes": ["no_override"],
            },
            options=options,
            grant_type="{{ config['grant_type'] }}"
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
            options={},
        )

        resp.status_code = 200
        mocker.patch.object(resp, "json", return_value={"access_token": "access_token", "expires_in": 1000})
        mocker.patch.object(requests, "request", side_effect=mock_request, autospec=True)
        token = oauth.refresh_access_token()

        schem = DeclarativeOauth2Authenticator.json_schema()
        print(schem)

        assert ("access_token", 1000) == token


def mock_request(method, url, data):
    if url == "refresh_end":
        return resp
    raise Exception(f"Error while refreshing access token with request: {method}, {url}, {data}")
