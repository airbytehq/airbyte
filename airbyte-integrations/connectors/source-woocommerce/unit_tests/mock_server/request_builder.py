# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Optional

from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import SHOP


def get_base_url(shop: str = SHOP) -> str:
    return f"https://{shop}/wp-json/wc/v3"


class WooCommerceRequestBuilder:
    @classmethod
    def orders_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="orders", shop=shop)

    @classmethod
    def products_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="products", shop=shop)

    @classmethod
    def customers_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="customers", shop=shop)

    @classmethod
    def coupons_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="coupons", shop=shop)

    @classmethod
    def product_categories_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="products/categories", shop=shop)

    @classmethod
    def order_notes_endpoint(cls, order_id: int, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource=f"orders/{order_id}/notes", shop=shop)

    @classmethod
    def product_variations_endpoint(cls, product_id: int, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource=f"products/{product_id}/variations", shop=shop)

    @classmethod
    def payment_gateways_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="payment_gateways", shop=shop)

    @classmethod
    def product_reviews_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="products/reviews", shop=shop)

    @classmethod
    def product_attributes_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="products/attributes", shop=shop)

    @classmethod
    def product_tags_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="products/tags", shop=shop)

    @classmethod
    def shipping_zones_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="shipping/zones", shop=shop)

    @classmethod
    def tax_classes_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="taxes/classes", shop=shop)

    @classmethod
    def tax_rates_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="taxes", shop=shop)

    @classmethod
    def product_shipping_classes_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="products/shipping_classes", shop=shop)

    @classmethod
    def shipping_methods_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="shipping_methods", shop=shop)

    @classmethod
    def system_status_tools_endpoint(cls, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource="system_status/tools", shop=shop)

    @classmethod
    def refunds_endpoint(cls, order_id: int, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource=f"orders/{order_id}/refunds", shop=shop)

    @classmethod
    def product_attribute_terms_endpoint(cls, attribute_id: int, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource=f"products/attributes/{attribute_id}/terms", shop=shop)

    @classmethod
    def shipping_zone_locations_endpoint(cls, zone_id: int, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource=f"shipping/zones/{zone_id}/locations", shop=shop)

    @classmethod
    def shipping_zone_methods_endpoint(cls, zone_id: int, shop: str = SHOP) -> WooCommerceRequestBuilder:
        return cls(resource=f"shipping/zones/{zone_id}/methods", shop=shop)

    def __init__(self, resource: str, shop: str = SHOP) -> None:
        self._resource = resource
        self._shop = shop
        self._query_params = {}

    def with_per_page(self, per_page: int) -> WooCommerceRequestBuilder:
        self._query_params["per_page"] = str(per_page)
        return self

    def with_offset(self, offset: int) -> WooCommerceRequestBuilder:
        self._query_params["offset"] = str(offset)
        return self

    def with_order(self, order: str) -> WooCommerceRequestBuilder:
        self._query_params["order"] = order
        return self

    def with_orderby(self, orderby: str) -> WooCommerceRequestBuilder:
        self._query_params["orderby"] = orderby
        return self

    def with_dates_are_gmt(self, value: str = "true") -> WooCommerceRequestBuilder:
        self._query_params["dates_are_gmt"] = value
        return self

    def with_modified_after(self, modified_after: str) -> WooCommerceRequestBuilder:
        self._query_params["modified_after"] = modified_after
        return self

    def with_modified_before(self, modified_before: str) -> WooCommerceRequestBuilder:
        self._query_params["modified_before"] = modified_before
        return self

    def with_after(self, after: str) -> WooCommerceRequestBuilder:
        self._query_params["after"] = after
        return self

    def with_before(self, before: str) -> WooCommerceRequestBuilder:
        self._query_params["before"] = before
        return self

    def with_default_params(self) -> WooCommerceRequestBuilder:
        return self.with_order("asc").with_orderby("id").with_dates_are_gmt("true").with_per_page(100)

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{get_base_url(self._shop)}/{self._resource}",
            query_params=self._query_params if self._query_params else None,
        )
