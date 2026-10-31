# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import pytest
from source_shopify.source import SourceShopify
from source_shopify.streams.streams import Shop
from source_shopify.utils import ShopifyWrongShopNameError

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


@pytest.mark.parametrize("auth_method,token_key", [("api_password", "api_password"), ("oauth2.0", "access_token")])
@pytest.mark.parametrize(
    "status,body,hints",
    [
        (401, '{"errors":"Invalid API key or access token"}', ["authentication failed", "Re-authenticate", "Admin API access token"]),
        (403, '{"errors":"Required access: read_products access scope"}', ["access is denied", "read_products"]),
        (403, '{"errors":"Requires read_orders and read_products"}', ["read_orders", "read_products"]),
        (403, "", ["required access scopes", "re-authorize"]),
        (403, "sensitive-response-value", ["required access scopes"]),
    ],
)
def test_check_authentication_and_scope_failures(basic_config, requests_mock, auth_method, token_key, status, body, hints) -> None:
    config = {**basic_config, "credentials": {"auth_method": auth_method, token_key: "fake-token"}}
    requests_mock.get(f"https://test-shop.myshopify.com/admin/api/{Shop.api_version}/shop.json", text=body, status_code=status)

    with pytest.raises(AirbyteTracedException) as raised:
        SourceShopify().check_connection(logging.getLogger("airbyte"), config)

    assert raised.value.failure_type == FailureType.config_error
    for hint in hints:
        assert hint in raised.value.message
    assert "sensitive-response-value" not in raised.value.message
    assert "fake-token" not in raised.value.message
    assert requests_mock.call_count == 1


@pytest.mark.parametrize("shop", ["test-shop", "test-shop.myshopify.com", "https://test-shop.myshopify.com/"])
def test_normalized_shop_is_used_by_check(basic_config, requests_mock, shop) -> None:
    config = {**basic_config, "shop": shop}
    requests_mock.get(f"https://test-shop.myshopify.com/admin/api/{Shop.api_version}/shop.json", json={"shop": {"id": 1}})
    assert SourceShopify().check_connection(logging.getLogger("airbyte"), config) == (True, None)
    assert config["shop"] == "test-shop"


@pytest.mark.parametrize("status", [402, 404])
def test_check_preserves_other_nonretryable_errors(basic_config, requests_mock, status) -> None:
    requests_mock.get(f"https://test-shop.myshopify.com/admin/api/{Shop.api_version}/shop.json", json={}, status_code=status)
    success, message = SourceShopify().check_connection(logging.getLogger("airbyte"), basic_config)
    assert not success
    assert "Verify the entered Shopify store" in message
    assert requests_mock.call_count == 1


@pytest.mark.parametrize(
    "shop",
    [
        "https://test-shop.myshopify.com/admin",
        "ftp://test-shop.myshopify.com",
        "https://[invalid",
        "https://user:secret@test-shop.myshopify.com",
        "https://test-shop.myshopify.com?token=secret",
        "https://test-shop.myshopify.com.evil.example",
        "https://test-shop.myshopify.com:443",
        "garbage /input",
        "",
        None,
    ],
)
def test_invalid_shop_fails_before_request(basic_config, requests_mock, shop) -> None:
    config = {**basic_config, "shop": shop}
    success, message = SourceShopify().check_connection(logging.getLogger("airbyte"), config)
    assert not success
    assert "Enter the store handle" in message
    assert "secret" not in message
    assert requests_mock.call_count == 0
    with pytest.raises(ShopifyWrongShopNameError) as raised:
        SourceShopify.get_shop_name(config)
    assert raised.value.failure_type == FailureType.config_error
