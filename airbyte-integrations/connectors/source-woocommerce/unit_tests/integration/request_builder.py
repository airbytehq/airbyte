#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import List, Optional, Union

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.test.mock_http.request import HttpRequest
from source_woocommerce import SourceWoocommerce


def _get_base_url() -> str:
    base_url = resolve_manifest(source=SourceWoocommerce()).record.data["manifest"]["definitions"]["requester"]["url_base"]
    base_url = base_url.replace("{{ config['shop'] }}", "airbyte.store")
    return base_url


def get_customers_request() -> RequestBuilder:
    return RequestBuilder.get_customers_endpoint()


def get_coupons_request() -> RequestBuilder:
    return RequestBuilder.get_coupons_endpoint()


def get_orders_request() -> RequestBuilder:
    return RequestBuilder.get_orders_endpoint()


def get_order_notes_request(order_id: str) -> RequestBuilder:
    return RequestBuilder.get_order_notes_endpoint(order_id)


def get_payment_gateways_request() -> RequestBuilder:
    return RequestBuilder.get_payment_gateways_endpoint()


def get_product_attributes_request() -> RequestBuilder:
    return RequestBuilder.get_product_attributes_endpoint()


def get_product_attribute_terms_request(attribute_id: str) -> RequestBuilder:
    return RequestBuilder.get_product_attribute_terms_endpoint(attribute_id)


def get_product_categories_request() -> RequestBuilder:
    return RequestBuilder.get_product_categories_endpoint()


def get_product_reviews_request() -> RequestBuilder:
    return RequestBuilder.get_product_reviews_endpoint()


def get_product_shipping_classes_request() -> RequestBuilder:
    return RequestBuilder.get_product_shipping_classes_endpoint()


def get_product_tags_request() -> RequestBuilder:
    return RequestBuilder.get_product_tags_endpoint()


def get_products_request() -> RequestBuilder:
    return RequestBuilder.get_products_endpoint()


def get_product_variations_request(product_id: str) -> RequestBuilder:
    return RequestBuilder.get_product_variations_endpoint(product_id)


def get_refunds_request(order_id: str) -> RequestBuilder:
    return RequestBuilder.get_refunds_endpoint(order_id)


def get_shipping_methods_request() -> RequestBuilder:
    return RequestBuilder.get_shipping_methods_endpoint()


def get_shipping_zones_request() -> RequestBuilder:
    return RequestBuilder.get_shipping_zones_endpoint()


def get_shipping_zone_locations_request(zone_id: str) -> RequestBuilder:
    return RequestBuilder.get_shipping_zone_locations_endpoint(zone_id)


def get_shipping_zone_methods_request(zone_id: str) -> RequestBuilder:
    return RequestBuilder.get_shipping_zone_methods_endpoint(zone_id)


class RequestBuilder:
    @classmethod
    def get_customers_endpoint(cls) -> RequestBuilder:
        return cls(resource="customers")

    @classmethod
    def get_coupons_endpoint(cls) -> RequestBuilder:
        return cls(resource="coupons")

    @classmethod
    def get_orders_endpoint(cls) -> RequestBuilder:
        return cls(resource="orders")

    @classmethod
    def get_order_notes_endpoint(cls, order_id: str) -> RequestBuilder:
        return cls(resource=f"orders/{order_id}/notes")

    @classmethod
    def get_payment_gateways_endpoint(cls) -> RequestBuilder:
        return cls(resource="payment_gateways")

    @classmethod
    def get_product_attributes_endpoint(cls) -> RequestBuilder:
        return cls(resource="products/attributes")

    @classmethod
    def get_product_attribute_terms_endpoint(cls, attribute_id: str) -> RequestBuilder:
        return cls(resource=f"products/attributes/{attribute_id}/terms")

    @classmethod
    def get_product_categories_endpoint(cls) -> RequestBuilder:
        return cls(resource="products/categories")

    @classmethod
    def get_product_reviews_endpoint(cls) -> RequestBuilder:
        return cls(resource="products/reviews")

    @classmethod
    def get_product_shipping_classes_endpoint(cls) -> RequestBuilder:
        return cls(resource="products/shipping_classes")

    @classmethod
    def get_product_tags_endpoint(cls) -> RequestBuilder:
        return cls(resource="products/tags")

    @classmethod
    def get_products_endpoint(cls) -> RequestBuilder:
        return cls(resource="products")

    @classmethod
    def get_product_variations_endpoint(cls, product_id: str) -> RequestBuilder:
        return cls(resource=f"products/{product_id}/variations")

    @classmethod
    def get_refunds_endpoint(cls, order_id: str) -> RequestBuilder:
        return cls(resource=f"orders/{order_id}/refunds")

    @classmethod
    def get_shipping_methods_endpoint(cls) -> RequestBuilder:
        return cls(resource="shipping_methods")

    @classmethod
    def get_shipping_zones_endpoint(cls) -> RequestBuilder:
        return cls(resource="shipping/zones")

    @classmethod
    def get_shipping_zone_locations_endpoint(cls, zone_id: str) -> RequestBuilder:
        return cls(resource=f"shipping/zones/{zone_id}/locations")

    @classmethod
    def get_shipping_zone_methods_endpoint(cls, zone_id: str) -> RequestBuilder:
        return cls(resource=f"shipping/zones/{zone_id}/methods")

    def __init__(self, resource: Optional[str] = "") -> None:
        self._item_id = None
        self._resource = resource
        self._query_params = {}
        self._body = None
        self._item_id_is_sub_path = True

    def with_item_id(self, item_id: str) -> RequestBuilder:
        self._item_id = item_id
        return self

    def with_limit(self, limit: int) -> RequestBuilder:
        self._query_params["limit"] = limit
        return self

    def with_fields(self, fields: List[str]) -> RequestBuilder:
        self._query_params["fields"] = self._get_formatted_fields(fields)
        return self

    def with_next_page_token(self, next_page_token: str) -> RequestBuilder:
        self._query_params["after"] = next_page_token
        return self

    def with_item_id_is_sub_path(self, is_sub_path: bool):
        self._item_id_is_sub_path = is_sub_path
        return self

    def with_param(self, param: str, value: Union[str, List[str]], with_format=False):
        if with_format and isinstance(value, List):
            value = self._get_formatted_fields(value)
        self._query_params[param] = value
        return self

    @staticmethod
    def _get_formatted_fields(fields: List[str]) -> str:
        return ",".join(fields)

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{_get_base_url()}/{self._item_path()}{self._resource}",
            query_params=self._query_params,
            body=self._body,
        )

    def _item_path(self) -> str:
        path_for_resource = "/" if self._item_id_is_sub_path else ""
        return f"{self._item_id}{path_for_resource}" if self._item_id else ""

