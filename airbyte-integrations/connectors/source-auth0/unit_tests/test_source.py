#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator
from source_auth0.authenticator import Auth0Oauth2Authenticator
from source_auth0.source import SourceAuth0, Users, initialize_authenticator


class TestAuthentication:
    def test_init_token_authentication_init(self, token_config):
        token_auth = initialize_authenticator(config=token_config)
        assert isinstance(token_auth, TokenAuthenticator)

    def test_init_oauth2_authentication_init(self, oauth_config):
        oauth_auth = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_auth, Auth0Oauth2Authenticator)

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

    def test_check_connection_ok(self, requests_mock, oauth_config, url_base):
        oauth_auth = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_auth, Auth0Oauth2Authenticator)

        source_auth0 = SourceAuth0()
        requests_mock.get(f"{url_base}/api/v2/users?per_page=1", json={"connect": "ok"})
        requests_mock.post(f"{url_base}/oauth/token", json={"access_token": "test_token", "expires_in": 948})
        assert source_auth0.check_connection(logger=MagicMock(), config=oauth_config) == (True, None)

    def test_check_connection_error_status_code(self, requests_mock, oauth_config, url_base):
        oauth_auth = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_auth, Auth0Oauth2Authenticator)

        source_auth0 = SourceAuth0()
        requests_mock.get(f"{url_base}/api/v2/users?per_page=1", status_code=400, json={})
        requests_mock.post(f"{url_base}/oauth/token", json={"access_token": "test_token", "expires_in": 948})

        assert source_auth0.check_connection(logger=MagicMock(), config=oauth_config) == (False, {})

    def test_check_connection_error_with_exception(
        self, requests_mock, oauth_config, url_base, error_failed_to_authorize_with_provided_credentials
    ):
        oauth_auth = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_auth, Auth0Oauth2Authenticator)

        source_auth0 = SourceAuth0()
        requests_mock.get(f"{url_base}/api/v2/users?per_page=1", status_code=400, json="ss")
        requests_mock.post(f"{url_base}/oauth/token", json={"access_token": "test_token", "expires_in": 948})

        assert source_auth0.check_connection(logger=MagicMock(), config="wrong_config") == (
            False,
            error_failed_to_authorize_with_provided_credentials,
        )

    def test_check_streams(self, requests_mock, oauth_config, api_url):
        oauth_auth = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_auth, Auth0Oauth2Authenticator)

        source_auth0 = SourceAuth0()
        requests_mock.get(f"{api_url}/api/v2/users?per_page=1", json={"connect": "ok"})
        requests_mock.post(f"{api_url}/oauth/token", json={"access_token": "test_token", "expires_in": 948})
        streams = source_auth0.streams(config=oauth_config)
        for i, _ in enumerate([Users]):
            assert isinstance(streams[i], _)
