# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.mock_http.response_builder import find_template

_ALL_SCOPES = [
    "read_all_cart_transforms",
    "read_all_checkout_completion_target_customizations",
    "read_all_orders",
    "read_analytics",
    "read_assigned_fulfillment_orders",
    "read_cart_transforms",
    "read_channels",
    "read_companies",
    "read_content",
    "read_custom_fulfillment_services",
    "read_customer_data_erasure",
    "read_customer_merge",
    "read_customers",
    "read_dery_customizations",
    "read_discounts",
    "read_draft_orders",
    "read_files",
    "read_fulfillment_constraint_rules",
    "read_fulfillments",
    "read_gates",
    "read_gdpr_data_request",
    "read_gift_cards",
    "read_inventory",
    "read_legal_policies",
    "read_locales",
    "read_locations",
    "read_marketing_events",
    "read_markets",
    "read_merchant_managed_fulfillment_orders",
    "read_online_store_navigation",
    "read_online_store_pages",
    "read_order_edits",
    "read_order_submission_rules",
    "read_orders",
    "read_packing_slip_templates",
    "read_payment_customizations",
    "read_payment_terms",
    "read_pixels",
    "read_price_rules",
    "read_product_feeds",
    "read_product_listings",
    "read_products",
    "read_publications",
    "read_purchase_options",
    "read_reports",
    "read_resource_feedbacks",
    "read_returns",
    "read_script_tags",
    "read_shipping",
    "read_shopify_credit",
    "read_shopify_payments_accounts",
    "read_shopify_payments_bank_accounts",
    "read_shopify_payments_disputes",
    "read_shopify_payments_payouts",
    "read_shopify_payments_provider_accounts_sensitive",
    "read_store_credit_account_transactions",
    "read_themes",
    "read_third_party_fulfillment_orders",
    "read_translations"
]


def set_up_shop(http_mocker: HttpMocker, shop_name: str) -> None:
    http_mocker.get(
        HttpRequest(f"https://{shop_name}.myshopify.com/admin/api/2023-07/shop.json", query_params=ANY_QUERY_PARAMS),
        HttpResponse(json.dumps(find_template("shop", __file__)), status_code=200),
    )


def grant_all_scopes(http_mocker: HttpMocker, shop_name: str) -> None:
    http_mocker.get(
        HttpRequest(f"https://{shop_name}.myshopify.com/admin/oauth/access_scopes.json"),
        HttpResponse(json.dumps({"access_scopes": [{"handle": scope} for scope in _ALL_SCOPES]}), status_code=200),
    )
