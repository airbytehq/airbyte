#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from source_okta.components import CustomBearerAuthenticator, CustomOauth2Authenticator
from source_okta.source import SourceOkta


def get_oauth_keys(oauth_config):
    oauth_keys = {}
    oauth_keys["client_id"] = oauth_config["client_id"]


class TestAuthentication:
    def test_init_token_authentication_init(self, token_config, auth_token_config):
        token_authenticator_instance = CustomBearerAuthenticator(parameters=None, config=token_config)
        assert isinstance(token_authenticator_instance, CustomBearerAuthenticator)

        token_authenticator_instance = CustomBearerAuthenticator(parameters=None, config=auth_token_config)
        assert isinstance(token_authenticator_instance, CustomBearerAuthenticator)

    def test_init_oauth2_authentication_init(self, oauth_config):
        oauth_kwargs = {key: value for key, value in oauth_config.get("credentials").items() if key != "auth_type"}
        oauth_kwargs["token_refresh_endpoint"] = "https://okta.com/token-refresh"
        oauth_authentication_instance = CustomOauth2Authenticator(config=oauth_config, **oauth_kwargs, parameters=None)
        assert isinstance(oauth_authentication_instance, CustomOauth2Authenticator)

    def test_init_oauth2_authentication_wrong_credentials_record(self, wrong_oauth_config_bad_credentials_record):
        try:
            # Creating dummy kwargs so that the CustomOauth2Authenticator constructor does not throw errors
            oauth_kwargs = {
                "token_refresh_endpoint": "https://okta.com/token-refresh",
                "client_id": "abc",
                "client_secret": "def",
                "refresh_token": "ghi",
            }
            CustomOauth2Authenticator(config=wrong_oauth_config_bad_credentials_record, **oauth_kwargs, parameters=None)
        except Exception as e:
            assert e.args[0] == "Config validation error. `credentials` not specified."

    def test_init_oauth2_authentication_wrong_oauth_config_bad_auth_type(self, wrong_oauth_config_bad_auth_type):
        try:
            # Creating dummy kwargs so that the CustomOauth2Authenticator constructor does not throw errors
            oauth_kwargs = {
                "token_refresh_endpoint": "https://okta.com/token-refresh",
                "client_id": "abc",
                "client_secret": "def",
                "refresh_token": "ghi",
            }
            CustomOauth2Authenticator(config=wrong_oauth_config_bad_auth_type, **oauth_kwargs, parameters=None)
        except Exception as e:
            assert e.args[0] == "Config validation error. `auth_type` not specified."

    def test_check_streams(self, requests_mock, oauth_config, api_url):
        oauth_kwargs = {key: value for key, value in oauth_config.get("credentials").items() if key != "auth_type"}
        oauth_kwargs["token_refresh_endpoint"] = f"{api_url}/oauth2/v1/token"
        oauth_authentication_instance = CustomOauth2Authenticator(config=oauth_config, **oauth_kwargs, parameters=None)
        assert isinstance(oauth_authentication_instance, CustomOauth2Authenticator)
        source_okta = SourceOkta()
        streams = source_okta.streams(config=oauth_config)
        for i, _ in enumerate(streams):
            assert _.__class__.__name__ == "DeclarativeStream"

    def test_oauth2_refresh_token_ok(self, requests_mock, oauth_config, api_url):
        oauth_kwargs = {key: value for key, value in oauth_config.get("credentials").items() if key != "auth_type"}
        oauth_kwargs["token_refresh_endpoint"] = f"{api_url}/oauth2/v1/token"
        oauth_authentication_instance = CustomOauth2Authenticator(config=oauth_config, **oauth_kwargs, parameters=None)
        assert isinstance(oauth_authentication_instance, CustomOauth2Authenticator)
        oauth_authentication_instance.path = f"{api_url}/oauth2/v1/token"
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})
        result = oauth_authentication_instance.refresh_access_token()
        assert result == ("test_token", 948)

    def test_oauth2_refresh_token_failed(self, requests_mock, oauth_config, api_url, error_while_refreshing_access_token):
        oauth_kwargs = {key: value for key, value in oauth_config.get("credentials").items() if key != "auth_type"}
        oauth_kwargs["token_refresh_endpoint"] = f"{api_url}/oauth2/v1/token"
        oauth_authentication_instance = CustomOauth2Authenticator(config=oauth_config, **oauth_kwargs, parameters=None)
        assert isinstance(oauth_authentication_instance, CustomOauth2Authenticator)
        oauth_authentication_instance.path = f"{api_url}/oauth2/v1/token"
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"token": "test_token", "expires_in": 948})
        try:
            oauth_authentication_instance.refresh_access_token()
        except Exception as e:
            assert e.args[0] == error_while_refreshing_access_token
