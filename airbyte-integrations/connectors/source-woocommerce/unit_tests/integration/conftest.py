from airbyte_cdk.test.utils.data import get_json_contents
from .common import build_url


def orders_http_calls():
    return [
        {
            "request": {
                "url": build_url("orders", modified_after=".+", modified_before=".+", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("orders.json", __file__)},
        },
    ]


def coupons_http_calls():
    return [
        {
            "request": {
                "url": build_url("coupons", modified_after=".+", modified_before=".+", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("coupons.json", __file__)},
        },
    ]


def customers_http_calls():
    return [
        {
            "request": {
                "url": build_url("customers"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("customers.json", __file__)},
        },
    ]


def payment_gateways_http_calls():
    return [
        {
            "request": {
                "url": build_url("payment_gateways"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("payment_gateways.json", __file__)},
        },
    ]


def product_attributes_http_calls():
    return [
        {
            "request": {
                "url": build_url("products/attributes"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("product_attributes.json", __file__)},
        },
    ]


def product_categories_http_calls():
    return [
        {
            "request": {
                "url": build_url("products/categories"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("product_categories.json", __file__)},
        },
    ]


def product_reviews_http_calls():
    return [
        {
            "request": {
                "url": build_url("products/reviews"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("product_reviews.json", __file__)},
        },
    ]


def products_http_calls():
    return [
        {
            "request": {
                "url": build_url("products", modified_after=".+", modified_before=".+", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("products.json", __file__)},
        },
    ]


def product_shipping_classes_http_calls():
    return [
        {
            "request": {
                "url": build_url("products/shipping_classes"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("product_shipping_classes.json", __file__)},
        },
    ]


def product_tags_http_calls():
    return [
        {
            "request": {
                "url": build_url("products/tags"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("product_tags.json", __file__)},
        },
    ]


def shipping_methods_http_calls():
    return [
        {
            "request": {
                "url": build_url("shipping_methods"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("shipping_methods.json", __file__)},
        },
    ]


def shipping_zones_http_calls():
    return [
        {
            "request": {
                "url": build_url("shipping/zones"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("shipping_zones.json", __file__)},
        },
    ]


def system_status_tools_http_calls():
    return [
        {
            "request": {
                "url": build_url("system_status/tools"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("system_status_tools.json", __file__)},
        },
    ]


def order_notes_http_calls():
    return [
        {
            "request": {
                "url": build_url("orders", modified_after="2017-01-01T00:00:00", modified_before="2017-01-29T00:00:00"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("orders.json", __file__)},
        },
        {
            "request": {
                "url": build_url("orders/(727|723)/notes", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("order_notes.json", __file__)},
        },
    ]


def product_attribute_terms_http_calls():
    return [
        {
            "request": {
                "url": build_url("products/attributes"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("product_attributes.json", __file__)},
        },
        {
            "request": {
                "url": build_url("products/attributes/.+/terms", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("product_attribute_terms.json", __file__)},
        },
    ]


def product_variations_http_calls():
    return [
        {
            "request": {
                "url": build_url("products"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("products.json", __file__)},
        },
        {
            "request": {
                "url": build_url("products/(799|794)/variations", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("product_variations.json", __file__)},
        },
    ]


def refunds_http_calls():
    return [
        {
            "request": {
                "url": build_url("orders"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("orders.json", __file__)},
        },
        {
            "request": {
                "url": build_url("orders/(727|723)/refunds", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("refunds.json", __file__)},
        },
    ]


def shipping_zone_locations_http_calls():
    return [
        {
            "request": {
                "url": build_url("shipping/zones"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("shipping_zones.json", __file__)},
        },
        {
            "request": {
                "url": build_url("shipping/zones/(0|5)/locations", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("shipping_zone_locations.json", __file__)},
        },
    ]


def shipping_zone_methods_http_calls():
    return [
        {
            "request": {
                "url": build_url("shipping/zones"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("shipping_zones.json", __file__)},
        },
        {
            "request": {
                "url": build_url("shipping/zones/(0|5)/methods", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("shipping_zone_methods.json", __file__)},
        },
    ]


def tax_classes_http_calls():
    return [
        {
            "request": {
                "url": build_url("taxes/classes"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("tax_classes.json", __file__)},
        },
    ]


def tax_rates_http_calls():
    return [
        {
            "request": {
                "url": build_url("taxes"),
                "is_regex": False
            },
            "response": {"text": get_json_contents("tax_rates.json", __file__)},
        },
    ]


def orders_empty_last_page():
    return [
        {
            "request": {
                "url": build_url("orders", modified_after=".+", modified_before=".+", is_regex=True),
                "is_regex": True
            },
            "response": {"text": get_json_contents("orders.json", __file__)},
        },
        {
            "request": {
                "url": build_url("orders", modified_after=".+", modified_before=".+", is_regex=True),
                "is_regex": True
            },
            "response": {"text": "[]"},
        },
    ]
