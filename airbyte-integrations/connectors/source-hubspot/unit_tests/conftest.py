#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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


@pytest.fixture(name="config_invalid_client_id")
def config_invalid_client_id_fixture():
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "client_id": "invalid_client_id",
            "client_secret": "invalid_client_secret",
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        },
    }


@pytest.fixture(name="config")
def config_fixture():
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
        "enable_experimental_streams": False,
    }


@pytest.fixture(name="config_experimental")
def config_eperimantal_fixture():
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
        "enable_experimental_streams": True,
    }


@pytest.fixture(name="config_invalid_date")
def config_invalid_date_fixture():
    return {
        "start_date": "2000-00-00T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
    }


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"credentials_title": "Private App Credentials", "access_token": "wrong token"}


@pytest.fixture(name="fake_properties_list")
def fake_properties_list():
    return [f"property_number_{i}" for i in range(NUMBER_OF_PROPERTIES)]


@pytest.fixture(name="migrated_properties_list")
def migrated_properties_list():
    return [
        "hs_v2_date_entered_prospect",
        "hs_v2_date_exited_prospect",
        "hs_v2_cumulative_time_in_prsopect",
        "hs_v2_some_other_property_in_prospect",
    ]


@pytest.fixture(name="api")
def api(some_credentials):
    return API(some_credentials)


@pytest.fixture
def http_mocker():
    return None
