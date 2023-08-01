#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_medallia.authenticator import MedalliaOauth2Authenticator


@pytest.fixture()
def url_base():
    """
    URL base for test
    """
    return "https://test_domain.okta.com"


@pytest.fixture()
def api_url(url_base):
    """
    Just return API url based on url_base
    """
    return f"{url_base}"


@pytest.fixture()
def oauth_config():
    """
    Credentials for oauth2.0 authorization
    """
    return {
        "credentials": {
            "token-endpoint": "oauth2.0",
            "clien-secret": "test_client_secret",
            "client-id": "test_client_id",
            "query-endpoint": "test_refresh_token",
        }
    }


@pytest.fixture()
def config():
    """
    Credentials for oauth2.0 authorization
    """

    auth = MedalliaOauth2Authenticator(
        token_endpoint="http://exampe",
        client_secret="test_client_secret",
        client_id="test_client_id"

    )

    initialization_params = {"authenticator": auth, "url_base": "http://query-endpoint"}

    return initialization_params


@pytest.fixture()
def wrong_oauth_config_bad_auth_type():
    """
    Wrong Credentials format for oauth2.0 authorization
    absent "auth_type" field
    """
    return {
        "credentials": {
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "domain": "test_domain",
    }
