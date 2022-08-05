#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import pathlib

import pytest
from source_paypal_transaction.source import PayPalOauth2Authenticator, SourcePaypalTransaction


@pytest.fixture()
def api_endpoint():
    return "https://api-m.paypal.com"


@pytest.fixture()
def sandbox_api_endpoint():
    return "https://api-m.sandbox.paypal.com"


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


@pytest.fixture(autouse=True)
def transactions(request):
    file = pathlib.Path(request.node.fspath.strpath)
    transaction = file.with_name("transaction.json")
    with transaction.open() as fp:
        return json.load(fp)


@pytest.fixture()
def prod_config():
    """
    Credentials for oauth2.0 authorization
    """
    return {
        "client_id": "some_client_id",
        "secret": "some_secret",
        "start_date": "2021-07-01T00:00:00+00:00",
        "end_date": "2021-07-10T00:00:00+00:00",
        "is_sandbox": False,
    }


@pytest.fixture()
def sandbox_config():
    """
    Credentials for oauth2.0 authorization
    """
    return {
        "client_id": "some_client_id",
        "secret": "some_secret",
        "start_date": "2021-07-01T00:00:00+00:00",
        "end_date": "2021-07-10T00:00:00+00:00",
        "is_sandbox": True,
    }


@pytest.fixture()
def new_prod_config():
    """
    Credentials for oauth2.0 authorization
    """
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "some_client_id",
            "client_secret": "some_client_secret",
            "refresh_token": "some_refresh_token",
        },
        "start_date": "2021-07-01T00:00:00+00:00",
        "end_date": "2021-07-10T00:00:00+00:00",
        "is_sandbox": False,
    }


@pytest.fixture()
def error_while_refreshing_access_token():
    """
    Error raised when using incorrect access token
    """
    return "Error while refreshing access token: 'access_token'"


@pytest.fixture()
def authenticator_instance(prod_config):
    return PayPalOauth2Authenticator(prod_config)


@pytest.fixture()
def new_format_authenticator_instance(new_prod_config):
    return PayPalOauth2Authenticator(new_prod_config)


@pytest.fixture()
def source_instance():
    return SourcePaypalTransaction()
