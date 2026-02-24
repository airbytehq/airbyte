#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import time

import pytest
import requests
from source_shopify.auth import ClientCredentialsAuthenticator, ClientCredentialsTokenError, NotImplementedAuth, ShopifyAuthenticator
from source_shopify.source import ConnectionCheckTest


TEST_ACCESS_TOKEN = "test_access_token"
TEST_API_PASSWORD = "test_api_password"
TEST_CLIENT_ID = "test_client_id"
TEST_CLIENT_SECRET = "test_client_secret"
TEST_SHOP = "test-shop"
TOKEN_URL = f"https://{TEST_SHOP}.myshopify.com/admin/oauth/access_token"


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
def config_client_credentials():
    return {
        "credentials": {
            "auth_method": "client_credentials",
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_CLIENT_SECRET,
            "shop": TEST_SHOP,
        }
    }


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


# --- ClientCredentialsAuthenticator._get_shop_name tests ---


@pytest.mark.parametrize(
    "config, expected_shop",
    [
        pytest.param(
            {"credentials": {"shop": "my-store"}},
            "my-store",
            id="shop_from_credentials",
        ),
        pytest.param(
            {"credentials": {"shop": "my-store.myshopify.com"}},
            "my-store",
            id="shop_from_credentials_strips_suffix",
        ),
        pytest.param(
            {"credentials": {}},
            "",
            id="empty_shop_returns_empty_string",
        ),
    ],
)
def test_client_credentials_get_shop_name(config, expected_shop):
    authenticator = ClientCredentialsAuthenticator(config=config)
    assert authenticator._get_shop_name() == expected_shop


# --- ClientCredentialsAuthenticator._exchange_credentials_for_token tests ---


def test_exchange_token_success(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"access_token": "new_token", "expires_in": 86400})
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    access_token, expiry_time = authenticator._exchange_credentials_for_token()
    assert access_token == "new_token"
    assert expiry_time > time.time()


def test_exchange_token_uses_default_expiry_when_missing(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"access_token": "new_token"})
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    before = time.time()
    access_token, expiry_time = authenticator._exchange_credentials_for_token()
    assert access_token == "new_token"
    assert expiry_time >= before + ClientCredentialsAuthenticator.DEFAULT_TOKEN_EXPIRY_SECONDS


@pytest.mark.parametrize(
    "credentials, expected_error_match",
    [
        pytest.param(
            {"client_secret": TEST_CLIENT_SECRET, "shop": TEST_SHOP},
            "Missing client_id or client_secret",
            id="missing_client_id",
        ),
        pytest.param(
            {"client_id": TEST_CLIENT_ID, "shop": TEST_SHOP},
            "Missing client_id or client_secret",
            id="missing_client_secret",
        ),
    ],
)
def test_exchange_token_missing_credentials(credentials, expected_error_match):
    config = {"credentials": credentials}
    authenticator = ClientCredentialsAuthenticator(config=config)
    with pytest.raises(ClientCredentialsTokenError, match=expected_error_match):
        authenticator._exchange_credentials_for_token()


@pytest.mark.parametrize(
    "status_code, expected_error_match",
    [
        pytest.param(401, "Invalid client credentials", id="401_invalid_credentials"),
        pytest.param(403, "Access denied", id="403_access_denied"),
        pytest.param(404, "not found", id="404_store_not_found"),
        pytest.param(500, "HTTP error 500", id="500_server_error"),
    ],
)
def test_exchange_token_http_errors(config_client_credentials, requests_mock, status_code, expected_error_match):
    requests_mock.post(TOKEN_URL, status_code=status_code)
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    with pytest.raises(ClientCredentialsTokenError, match=expected_error_match):
        authenticator._exchange_credentials_for_token()


def test_exchange_token_network_error(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, exc=requests.exceptions.ConnectionError)
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    with pytest.raises(ClientCredentialsTokenError, match="Network error"):
        authenticator._exchange_credentials_for_token()


def test_exchange_token_malformed_response(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"some_other_field": "value"})
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    with pytest.raises(ClientCredentialsTokenError, match="Missing or malformed access_token"):
        authenticator._exchange_credentials_for_token()


# --- ClientCredentialsAuthenticator.get_access_token tests ---


def test_get_access_token_fetches_on_first_call(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"access_token": "new_token", "expires_in": 86400})
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    assert authenticator.get_access_token() == "new_token"


def test_get_access_token_caches_token(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"access_token": "new_token", "expires_in": 86400})
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    token1 = authenticator.get_access_token()
    token2 = authenticator.get_access_token()
    assert token1 == token2 == "new_token"
    assert requests_mock.call_count == 1


@pytest.mark.parametrize(
    "expiry_offset, expected_call_count",
    [
        pytest.param(-1, 2, id="refreshes_when_expired"),
        pytest.param(100, 2, id="refreshes_within_buffer_window"),
        pytest.param(600, 1, id="no_refresh_when_not_near_expiry"),
    ],
)
def test_get_access_token_refresh_behavior(config_client_credentials, requests_mock, expiry_offset, expected_call_count):
    requests_mock.post(
        TOKEN_URL,
        [
            {"json": {"access_token": "token_1", "expires_in": 86400}},
            {"json": {"access_token": "token_2", "expires_in": 86400}},
        ],
    )
    authenticator = ClientCredentialsAuthenticator(config=config_client_credentials)
    authenticator.get_access_token()
    # Manipulate expiry to simulate different states
    authenticator._token_expiry = time.time() + expiry_offset
    authenticator.get_access_token()
    assert requests_mock.call_count == expected_call_count


# --- ShopifyAuthenticator client_credentials integration tests ---


def test_shopify_authenticator_lazy_inits_client_credentials(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"access_token": "cc_token", "expires_in": 86400})
    authenticator = ShopifyAuthenticator(config=config_client_credentials)
    assert authenticator._client_credentials_authenticator is None
    header = authenticator.get_auth_header()
    assert authenticator._client_credentials_authenticator is not None
    assert header == {"X-Shopify-Access-Token": "cc_token"}


def test_shopify_authenticator_reuses_client_credentials_instance(config_client_credentials, requests_mock):
    requests_mock.post(TOKEN_URL, json={"access_token": "cc_token", "expires_in": 86400})
    authenticator = ShopifyAuthenticator(config=config_client_credentials)
    authenticator.get_auth_header()
    first_instance = authenticator._client_credentials_authenticator
    authenticator.get_auth_header()
    assert authenticator._client_credentials_authenticator is first_instance
    assert requests_mock.call_count == 1
