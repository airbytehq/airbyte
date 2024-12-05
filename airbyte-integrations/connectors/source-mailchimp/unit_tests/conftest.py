#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="data_center")
def data_center_fixture():
    return "some_dc"


@fixture(name="config")
def config_fixture(data_center):
    return {"apikey": f"API_KEY-{data_center}", "start_date": "2022-01-01T00:00:00.000Z"}


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
