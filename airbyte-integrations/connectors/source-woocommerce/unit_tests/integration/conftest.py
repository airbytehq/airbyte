# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.utils.data import read_resource_file_contents

from .common import build_url


def request_response_mapping(stream_name, method="GET", custom_resource=None, is_regex=False, modified_after=None, modified_before=None,
                             custom_json_filename=None, status_code=200, response=None):
    """Create an HTTP request-response mapping for a stream."""
    json_filename = f"{stream_name}.json" if custom_json_filename is None else custom_json_filename
    resource = stream_name if custom_resource is None else custom_resource

    response_map = response
    if response is None:
        response_map = {"text": read_resource_file_contents(json_filename, __file__), "status_code": status_code}

    return {
        "request": {
            "url": build_url(resource, modified_after=modified_after, modified_before=modified_before, is_regex=is_regex),
            "is_regex": is_regex,
            "method": method,
        },
        "response": response_map,
    }


def orders_http_calls():
    return [request_response_mapping("orders")]


def coupons_http_calls():
    return [request_response_mapping("coupons")]


def customers_http_calls():
    return [request_response_mapping("customers")]


def payment_gateways_http_calls():
    return [request_response_mapping("payment_gateways")]


def product_attributes_http_calls():
    return [request_response_mapping("product_attributes", custom_resource="products/attributes")]


def product_categories_http_calls():
    return [request_response_mapping("product_categories", custom_resource="products/categories")]


def product_reviews_http_calls():
    return [request_response_mapping("product_reviews", custom_resource="products/reviews")]


def products_http_calls():
    return [request_response_mapping("products")]


def product_shipping_classes_http_calls():
    return [request_response_mapping("product_shipping_classes", custom_resource="products/shipping_classes")]


def product_tags_http_calls():
    return [request_response_mapping("product_tags", custom_resource="products/tags")]


def shipping_methods_http_calls():
    return [request_response_mapping("shipping_methods", custom_resource="shipping_methods")]


def shipping_zones_http_calls():
    return [request_response_mapping("shipping_zones", custom_resource="shipping/zones")]


def system_status_tools_http_calls():
    return [request_response_mapping("system_status_tools", custom_resource="system_status/tools")]


def order_notes_http_calls():
    return [
        request_response_mapping("orders", modified_after="2017-01-01.+", modified_before="2017-01-29.+", is_regex=True),
        request_response_mapping("order_notes", custom_resource="orders/(727|723)/notes", is_regex=True),
    ]


def product_attribute_terms_http_calls():
    return [
        request_response_mapping("product_attributes", custom_resource="products/attributes"),
        request_response_mapping("product_attribute_terms", custom_resource="products/attributes/.+/terms", is_regex=True),
    ]


def product_variations_http_calls():
    return [
        request_response_mapping("products"),
        request_response_mapping("product_variations", custom_resource="products/(799|794)/variations", is_regex=True),
    ]


def refunds_http_calls():
    return [
        request_response_mapping("orders"),
        request_response_mapping("refunds", custom_resource="orders/(727|723)/refunds", is_regex=True),
    ]


def shipping_zone_locations_http_calls():
    return [
        request_response_mapping("shipping_zones", custom_resource="shipping/zones"),
        request_response_mapping("shipping_zone_locations", custom_resource="shipping/zones/(0|5)/locations", is_regex=True),
    ]


def shipping_zone_methods_http_calls():
    return [
        request_response_mapping("shipping_zones", custom_resource="shipping/zones"),
        request_response_mapping("shipping_zone_methods", custom_resource="shipping/zones/(0|5)/methods", is_regex=True),
    ]


def tax_classes_http_calls():
    return [request_response_mapping("tax_classes", custom_resource="taxes/classes")]


def tax_rates_http_calls():
    return [request_response_mapping("tax_rates", custom_resource="taxes")]


def orders_empty_last_page():
    return [
        request_response_mapping("orders", is_regex=True, modified_after=".+", modified_before="2017-01-30.+"),
        request_response_mapping("orders", is_regex=True, modified_after=".+", modified_before="2017-02-10.+", response={"text": "[]"}),
    ]
