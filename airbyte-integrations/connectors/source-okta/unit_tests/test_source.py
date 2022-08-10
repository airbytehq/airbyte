#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_okta.authenticator import OktaOauth2Authenticator
from source_okta.source import (
    CustomRoles,
    GroupMembers,
    GroupRoleAssignments,
    Groups,
    Logs,
    SourceOkta,
    UserRoleAssignments,
    Users,
    initialize_authenticator,
)


class TestAuthentication:
    def test_init_token_authentication_init(self, token_config, auth_token_config):
        token_authenticator_instance = initialize_authenticator(config=token_config)
        assert isinstance(token_authenticator_instance, TokenAuthenticator)

        token_authenticator_instance = initialize_authenticator(config=auth_token_config)
        assert isinstance(token_authenticator_instance, TokenAuthenticator)

    def test_init_oauth2_authentication_init(self, oauth_config):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)

    def test_init_oauth2_authentication_wrong_credentials_record(self, wrong_oauth_config_bad_credentials_record):
        try:
            initialize_authenticator(config=wrong_oauth_config_bad_credentials_record)
        except Exception as e:
            assert e.args[0] == "Config validation error. `credentials` not specified."

    def test_init_oauth2_authentication_wrong_oauth_config_bad_auth_type(self, wrong_oauth_config_bad_auth_type):
        try:
            initialize_authenticator(config=wrong_oauth_config_bad_auth_type)
        except Exception as e:
            assert e.args[0] == "Config validation error. `auth_type` not specified."

    def test_check_connection_ok(self, requests_mock, oauth_config, api_url):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)

        source_okta = SourceOkta()
        requests_mock.get(f"{api_url}/api/v1/users?limit=1", json={"connect": "ok"})
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})
        assert source_okta.check_connection(logger=MagicMock(), config=oauth_config) == (True, None)

    def test_check_connection_error_status_code(self, requests_mock, oauth_config, api_url):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)

        source_okta = SourceOkta()
        requests_mock.get(f"{api_url}/api/v1/users?limit=1", status_code=400, json={})
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})

        assert source_okta.check_connection(logger=MagicMock(), config=oauth_config) == (False, {})

    def test_check_connection_error_with_exception(
        self, requests_mock, oauth_config, api_url, error_failed_to_authorize_with_provided_credentials
    ):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)

        source_okta = SourceOkta()
        requests_mock.get(f"{api_url}/api/v1/users?limit=1", status_code=400, json="ss")
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})

        assert source_okta.check_connection(logger=MagicMock(), config="wrong_config") == (
            False,
            error_failed_to_authorize_with_provided_credentials,
        )

    def test_check_streams(self, requests_mock, oauth_config, api_url):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)

        source_okta = SourceOkta()
        requests_mock.get(f"{api_url}/api/v1/users?limit=1", json={"connect": "ok"})
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})
        streams = source_okta.streams(config=oauth_config)
        for i, _ in enumerate([Groups, Logs, Users, GroupMembers, CustomRoles, UserRoleAssignments, GroupRoleAssignments]):
            assert isinstance(streams[i], _)

    def test_oauth2_refresh_token_ok(self, requests_mock, oauth_config, api_url):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})
        result = oauth_authentication_instance.refresh_access_token()
        assert result == ("test_token", 948)

    def test_oauth2_refresh_token_failed(self, requests_mock, oauth_config, api_url, error_while_refreshing_access_token):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, OktaOauth2Authenticator)
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"token": "test_token", "expires_in": 948})
        try:
            oauth_authentication_instance.refresh_access_token()
        except Exception as e:
            assert e.args[0] == error_while_refreshing_access_token
