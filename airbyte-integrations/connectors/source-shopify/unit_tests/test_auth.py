#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from urllib.parse import parse_qs

import orjson
import pytest
from source_shopify.auth import (
    NotImplementedAuth,
    ShopifyAuthenticator,
    ShopifyOAuth2Authenticator,
    build_shopify_authenticator,
)
from source_shopify.source import ConnectionCheckTest

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.models import AirbyteMessageSerializer


TEST_ACCESS_TOKEN = "test_access_token"
TEST_API_PASSWORD = "test_api_password"
TEST_REFRESH_TOKEN = "test_refresh_token"
TEST_CLIENT_ID = "test_client_id"
TEST_CLIENT_SECRET = "test_client_secret"


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


@pytest.mark.parametrize(
    "config,expected_type",
    [
        pytest.param(
            {
                "shop": "my-store",
                "credentials": {"auth_method": "oauth2.0", "access_token": TEST_ACCESS_TOKEN},
            },
            ShopifyAuthenticator,
            id="oauth2_static_token_no_refresh",
        ),
        pytest.param(
            {
                "shop": "my-store",
                "credentials": {"auth_method": "access_token", "access_token": TEST_ACCESS_TOKEN},
            },
            ShopifyAuthenticator,
            id="access_token_method",
        ),
        pytest.param(
            {
                "shop": "my-store",
                "credentials": {"auth_method": "api_password", "api_password": TEST_API_PASSWORD},
            },
            ShopifyAuthenticator,
            id="api_password_method",
        ),
        pytest.param(
            {
                "shop": "my-store",
                "credentials": {
                    "auth_method": "oauth2.0",
                    "access_token": TEST_ACCESS_TOKEN,
                    "refresh_token": TEST_REFRESH_TOKEN,
                    "token_expiry_date": "2026-12-01T00:00:00Z",
                    "client_id": TEST_CLIENT_ID,
                    "client_secret": TEST_CLIENT_SECRET,
                },
            },
            ShopifyOAuth2Authenticator,
            id="oauth2_expiring_token_with_refresh",
        ),
    ],
)
def test_build_shopify_authenticator(config, expected_type):
    authenticator = build_shopify_authenticator(config)
    assert isinstance(authenticator, expected_type)


def test_oauth2_authenticator_uses_shopify_header():
    config = {
        "shop": "my-store",
        "credentials": {
            "auth_method": "oauth2.0",
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": TEST_REFRESH_TOKEN,
            "token_expiry_date": "2099-12-31T23:59:59Z",
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_CLIENT_SECRET,
        },
    }
    authenticator = build_shopify_authenticator(config)
    assert isinstance(authenticator, ShopifyOAuth2Authenticator)
    header = authenticator.get_auth_header()
    assert "X-Shopify-Access-Token" in header
    assert header["X-Shopify-Access-Token"] == TEST_ACCESS_TOKEN
    assert "Authorization" not in header


def test_oauth2_authenticator_refresh_endpoint():
    config = {
        "shop": "my-store",
        "credentials": {
            "auth_method": "oauth2.0",
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": TEST_REFRESH_TOKEN,
            "token_expiry_date": "2099-12-31T23:59:59Z",
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_CLIENT_SECRET,
        },
    }
    authenticator = build_shopify_authenticator(config)
    assert authenticator.get_token_refresh_endpoint() == "https://my-store.myshopify.com/admin/oauth/access_token"


def test_oauth2_authenticator_reads_config_paths():
    config = {
        "shop": "my-store",
        "credentials": {
            "auth_method": "oauth2.0",
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": TEST_REFRESH_TOKEN,
            "token_expiry_date": "2099-12-31T23:59:59Z",
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_CLIENT_SECRET,
        },
    }
    authenticator = build_shopify_authenticator(config)
    assert authenticator.get_refresh_token() == TEST_REFRESH_TOKEN
    assert authenticator.get_client_id() == TEST_CLIENT_ID
    assert authenticator.get_client_secret() == TEST_CLIENT_SECRET


def _expiring_oauth_config():
    return {
        "shop": "my-store",
        "credentials": {
            "auth_method": "oauth2.0",
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": TEST_REFRESH_TOKEN,
            "token_expiry_date": "2020-01-01T00:00:00Z",
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_CLIENT_SECRET,
        },
    }


def test_oauth2_authenticator_refreshes_expired_token(requests_mock):
    config = _expiring_oauth_config()
    # Mimic source.py: the authenticator is stored back into the same config dict, and
    # streams() adds a runtime-only `shop_id`. The factory must snapshot the config so these
    # non-serializable / internal keys never end up in the emitted control message.
    config["authenticator"] = build_shopify_authenticator(config)
    config["shop_id"] = 123456
    authenticator = config["authenticator"]

    refresh_mock = requests_mock.post(
        "https://my-store.myshopify.com/admin/oauth/access_token",
        json={"access_token": "new_access_token", "expires_in": 3600, "refresh_token": "rotated_refresh_token"},
    )

    # Expired token forces a refresh, which rotates the tokens and emits a control message.
    assert authenticator.get_access_token() == "new_access_token"

    request_body = parse_qs(refresh_mock.last_request.text)
    assert request_body["grant_type"] == ["refresh_token"]
    assert request_body["client_id"] == [TEST_CLIENT_ID]
    assert request_body["client_secret"] == [TEST_CLIENT_SECRET]
    assert request_body["refresh_token"] == [TEST_REFRESH_TOKEN]

    # The rotated refresh token and new expiry are written back to the config paths.
    assert authenticator.get_refresh_token() == "rotated_refresh_token"
    assert authenticator.access_token == "new_access_token"
    assert authenticator._connector_config["credentials"]["token_expiry_date"] != "2020-01-01T00:00:00Z"


def test_oauth2_authenticator_control_message_is_serializable(requests_mock):
    """Regression test: the emitted config control message must be JSON-serializable.

    If the factory shared the live `config` dict with the authenticator, the authenticator
    object stored under `config["authenticator"]` would be serialized into the control message
    and crash `orjson.dumps` on the first refresh.
    """
    config = _expiring_oauth_config()
    config["authenticator"] = build_shopify_authenticator(config)
    config["shop_id"] = 123456
    authenticator = config["authenticator"]

    requests_mock.post(
        "https://my-store.myshopify.com/admin/oauth/access_token",
        json={"access_token": "new_access_token", "expires_in": 3600, "refresh_token": "rotated_refresh_token"},
    )
    authenticator.refresh_and_set_access_token()

    emitted_config = authenticator._connector_config
    assert "authenticator" not in emitted_config
    assert "shop_id" not in emitted_config

    message = create_connector_config_control_message(emitted_config)
    # Serializes the same way the CDK emits the control message to stdout.
    orjson.dumps(AirbyteMessageSerializer.dump(message))
