#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture
from source_mailchimp.source import MailChimpAuthenticator


@fixture(name="data_center")
def data_center_fixture():
    return "some_dc"


@fixture(name="config")
def config_fixture(data_center):
    return {"apikey": f"API_KEY-{data_center}"}


@fixture(name="access_token")
def access_token_fixture():
    return "some_access_token"


@fixture(name="oauth_config")
def oauth_config_fixture(access_token):
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "111111111",
            "client_secret": "secret_1111111111",
            "access_token": access_token,
        }
    }


@fixture(name="apikey_config")
def apikey_config_fixture(data_center):
    return {"credentials": {"auth_type": "apikey", "apikey": f"some_api_key-{data_center}"}}


@fixture(name="wrong_config")
def wrong_config_fixture():
    return {"credentials": {"auth_type": "not auth_type"}}


@fixture(name="auth")
def authenticator_fixture(apikey_config):
    return MailChimpAuthenticator().get_auth(apikey_config)
