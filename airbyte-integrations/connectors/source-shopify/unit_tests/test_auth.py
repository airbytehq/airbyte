#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_shopify.auth import NotImplementedAuth, ShopifyAuthenticator
from source_shopify.source import ConnectionCheckTest


TEST_ACCESS_TOKEN = "test_access_token"
TEST_API_PASSWORD = "test_api_password"


@pytest.fixture
def config_access_token():
    return {"credentials": {"access_token": TEST_ACCESS_TOKEN, "auth_method": "access_token"}}


@pytest.fixture
def config_api_password():
    return {"credentials": {"api_password": TEST_API_PASSWORD, "auth_method": "api_password"}}


@pytest.fixture
def config_not_implemented_auth_method():
    return {"credentials": {"auth_method": "not_implemented_auth_method"}}


@pytest.fixture
def config_missing_access_token():
    return {"shop": "SHOP_NAME", "credentials": {"auth_method": "oauth2.0", "access_token": None}}


@pytest.fixture
def expected_auth_header_access_token():
    return {"X-Shopify-Access-Token": TEST_ACCESS_TOKEN}


@pytest.fixture
def expected_auth_header_api_password():
    return {"X-Shopify-Access-Token": TEST_API_PASSWORD}


def test_shopify_authenticator_access_token(config_access_token, expected_auth_header_access_token):
    authenticator = ShopifyAuthenticator(config=config_access_token)
    assert authenticator.get_auth_header() == expected_auth_header_access_token


def test_shopify_authenticator_api_password(config_api_password, expected_auth_header_api_password):
    authenticator = ShopifyAuthenticator(config=config_api_password)
    assert authenticator.get_auth_header() == expected_auth_header_api_password


def test_raises_notimplemented_auth(config_not_implemented_auth_method):
    authenticator = ShopifyAuthenticator(config=(config_not_implemented_auth_method))
    with pytest.raises(NotImplementedAuth):
        authenticator.get_auth_header()


def test_raises_missing_access_token(config_missing_access_token):
    config_missing_access_token["authenticator"] = ShopifyAuthenticator(config=(config_missing_access_token))
    failed_check = ConnectionCheckTest(config_missing_access_token).test_connection()
    assert failed_check == (
        False,
        "Authentication was unsuccessful. Please verify your authentication credentials or login is correct.",
    )
