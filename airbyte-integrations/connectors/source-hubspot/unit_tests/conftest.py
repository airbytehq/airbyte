#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_hubspot.source import SourceHubspot
from source_hubspot.streams import API

NUMBER_OF_PROPERTIES = 2000


@pytest.fixture(name="oauth_config")
def oauth_config_fixture():
    return {
        "start_date": "2021-10-10T00:00:00Z",
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "redirect_uri": "https://airbyte.io",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token",
            "token_expires": "2021-05-30T06:00:00Z",
        },
    }


@pytest.fixture(name="common_params")
def common_params_fixture(config):
    source = SourceHubspot()
    common_params = source.get_common_params(config=config)
    return common_params


@pytest.fixture(name="config")
def config_fixture():
    return {"start_date": "2021-01-10T00:00:00Z", "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"}}


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"credentials_title": "Private App Credentials", "access_token": "wrong token"}


@pytest.fixture(name="creds_with_wrong_permissions")
def creds_with_wrong_permissions():
    return {"credentials_title": "Private App Credentials", "access_token": "THIS-IS-THE-ACCESS_TOKEN"}


@pytest.fixture(name="fake_properties_list")
def fake_properties_list():
    return [f"property_number_{i}" for i in range(NUMBER_OF_PROPERTIES)]


@pytest.fixture(name="api")
def api(some_credentials):
    return API(some_credentials)
