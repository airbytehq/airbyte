#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpClient
from requests.exceptions import InvalidURL, JSONDecodeError

from .http_request import ShopifyErrorHandler
from .utils import ShopifyAccessScopesError, ShopifyBadJsonError, ShopifyWrongShopNameError

SCOPES_MAPPING: Mapping[str, set[str]] = {
    # SCOPE: read_customers
    "Customers": ("read_customers",),
    "MetafieldCustomers": ("read_customers",),
    "CustomerSavedSearch": ("read_customers",),
    "CustomerAddress": ("read_customers",),
    # SCOPE: read_orders
    "OrderAgreements": ("read_orders",),
    "Orders": ("read_orders",),
    "CustomerJourneySummary": ("read_orders",),
    "AbandonedCheckouts": ("read_orders",),
    "TenderTransactions": ("read_orders",),
    "Transactions": ("read_orders",),
    "TransactionsGraphql": ("read_orders",),
    "Fulfillments": ("read_orders",),
    "OrderRefunds": ("read_orders",),
    "OrderRisks": ("read_orders",),
    "MetafieldOrders": ("read_orders",),
    # SCOPE: read_draft_orders
    "DraftOrders": ("read_draft_orders",),
    "MetafieldDraftOrders": ("read_draft_orders",),
    # SCOPE: read_products
    "Products": ("read_products",),
    "ProductsGraphQl": ("read_products",),
    "MetafieldProducts": ("read_products",),
    "ProductImages": ("read_products",),
    "MetafieldProductImages": ("read_products",),
    "MetafieldProductVariants": ("read_products",),
    "CustomCollections": ("read_products",),
    "Collects": ("read_products",),
    "ProductVariants": ("read_products",),
    "MetafieldCollections": ("read_products",),
    "SmartCollections": ("read_products",),
    "MetafieldSmartCollections": ("read_products",),
    # SCOPE: read_products, read_publications
    "Collections": ("read_products", "read_publications"),
    # SCOPE: read_content
    "Pages": ("read_content",),
    "MetafieldPages": ("read_content",),
    # SCOPE: read_price_rules
    "PriceRules": ("read_price_rules",),
    # SCOPE: read_discounts
    "DiscountCodes": ("read_discounts",),
    # SCOPE: read_locations
    "Locations": ("read_locations",),
    "MetafieldLocations": ("read_locations",),
    # SCOPE: read_inventory
    "InventoryItems": ("read_inventory",),
    "InventoryLevels": ("read_inventory",),
    # SCOPE: read_merchant_managed_fulfillment_orders
    "FulfillmentOrders": ("read_merchant_managed_fulfillment_orders",),
    # SCOPE: read_shopify_payments_payouts
    "BalanceTransactions": ("read_shopify_payments_payouts",),
    "Disputes": ("read_shopify_payments_payouts",),
    # SCOPE: read_online_store_pages
    "Articles": ("read_online_store_pages",),
    "MetafieldArticles": ("read_online_store_pages",),
    "Blogs": ("read_online_store_pages",),
    "MetafieldBlogs": ("read_online_store_pages",),
}

ALWAYS_PERMITTED_STREAMS: List[str] = [
    "MetafieldShops",
    "Shop",
    "Countries",
]


class ShopifyScopes:

    # define default logger
    logger = logging.getLogger("airbyte")

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.permitted_streams: List[str] = list(ALWAYS_PERMITTED_STREAMS)
        self.not_permitted_streams: List[set[str, str]] = []
        self._error_handler = ShopifyErrorHandler()
        self._http_client = HttpClient("ShopifyScopes", self.logger, self._error_handler, session=requests.Session())

        self.user_scopes = self.get_user_scopes(config)
        # for each stream check the authenticated user has all scopes required
        self.get_streams_from_user_scopes()
        # log if there are streams missing scopes and should be omitted
        self.emit_missing_scopes()

    # template for the log message
    missing_scope_message: str = (
        "The stream `{stream}` could not be synced without the `{scope}` scope. Please check the `{scope}` is granted."
    )

    def get_user_scopes(self, config) -> list[Any]:
        url = f"https://{config['shop']}.myshopify.com/admin/oauth/access_scopes.json"
        headers = config["authenticator"].get_auth_header()
        try:
            _, response = self._http_client.send_request("GET", url, headers=headers, request_kwargs={})
            access_scopes = [scope.get("handle") for scope in response.json().get("access_scopes")]
        except InvalidURL:
            raise ShopifyWrongShopNameError(url)
        except JSONDecodeError as json_error:
            raise ShopifyBadJsonError(json_error)

        if access_scopes:
            return access_scopes
        else:
            raise ShopifyAccessScopesError(response)

    def log_missing_scope(self, not_permitted_stream: Mapping[str, Any]) -> str:
        stream_name, scope = not_permitted_stream
        self.logger.warning(self.missing_scope_message.format(stream=stream_name, scope=scope))

    def emit_missing_scopes(self) -> Optional[Iterable[List[str]]]:
        if len(self.not_permitted_streams) > 0:
            for not_permitted_stream in self.not_permitted_streams:
                self.log_missing_scope(not_permitted_stream)

    def get_permitted_streams(self) -> List[str]:
        # return the list of validated streams
        return self.permitted_streams

    def not_permitted_streams_names(self) -> List[str]:
        return [not_permitted[0] for not_permitted in self.not_permitted_streams]

    def stream_has_no_missing_scopes(self, stream_name: str) -> bool:
        return stream_name not in self.not_permitted_streams_names()

    def check_user_has_stream_scope(self, stream_name: str, scope: str) -> None:
        if scope not in self.user_scopes:
            self.not_permitted_streams.append((stream_name, scope))

    def register_permitted_stream(self, stream_name: str) -> None:
        # allow stream only if there is a complete match with required scopes
        if self.stream_has_no_missing_scopes(stream_name):
            self.permitted_streams.append(stream_name)

    def validate_stream_scopes(self, stream_name: str, scopes_required: str) -> None:
        for scope in scopes_required:
            self.check_user_has_stream_scope(stream_name, scope)

    def get_streams_from_user_scopes(self) -> None:
        # for each stream check the authenticated user has all scopes required
        for stream_name, stream_scopes in SCOPES_MAPPING.items():
            self.validate_stream_scopes(stream_name, stream_scopes)
            self.register_permitted_stream(stream_name)
