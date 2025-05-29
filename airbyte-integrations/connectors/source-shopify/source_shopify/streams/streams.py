#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from source_shopify.shopify_graphql.bulk.query import (
    Collection,
    CustomerAddresses,
    CustomerJourney,
    DeliveryProfile,
    DiscountCode,
    FulfillmentOrder,
    InventoryItem,
    InventoryLevel,
    MetafieldCollection,
    MetafieldCustomer,
    MetafieldDraftOrder,
    MetafieldLocation,
    MetafieldOrder,
    MetafieldProduct,
    MetafieldProductImage,
    MetafieldProductVariant,
    OrderAgreement,
    OrderRisk,
    Product,
    ProductImage,
    ProductVariant,
    ProfileLocationGroups,
    Transaction,
)
from source_shopify.utils import LimitReducingErrorHandler, ShopifyNonRetryableErrors

from airbyte_cdk import HttpSubStream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from .base_streams import (
    FullRefreshShopifyGraphQlBulkStream,
    IncrementalShopifyGraphQlBulkStream,
    IncrementalShopifyNestedStream,
    IncrementalShopifyStream,
    IncrementalShopifyStreamWithDeletedEvents,
    IncrementalShopifySubstream,
    MetafieldShopifySubstream,
    ShopifyStream,
)


class Articles(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "articles"
    cursor_field = "id"
    order_field = "id"
    filter_field = "since_id"
    deleted_events_api_name = "Article"


class MetafieldArticles(MetafieldShopifySubstream):
    parent_stream_class = Articles


class Blogs(IncrementalShopifyStreamWithDeletedEvents):
    cursor_field = "id"
    order_field = "id"
    data_field = "blogs"
    filter_field = "since_id"
    deleted_events_api_name = "Blog"


class MetafieldBlogs(MetafieldShopifySubstream):
    parent_stream_class = Blogs


class Customers(IncrementalShopifyStream):
    data_field = "customers"


class MetafieldCustomers(IncrementalShopifyGraphQlBulkStream):
    parent_stream_class = Customers
    bulk_query: MetafieldCustomer = MetafieldCustomer


class Orders(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "orders"
    deleted_events_api_name = "Order"
    initial_limit = 250

    def __init__(self, config: Mapping[str, Any]):
        self._error_handler = LimitReducingErrorHandler(
            max_retries=5,
            error_mapping=DEFAULT_ERROR_MAPPING | ShopifyNonRetryableErrors("orders"),
        )
        super().__init__(config)

    def request_params(self, stream_state=None, next_page_token=None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        params["limit"] = self.initial_limit  # Always start with the default limit; error handler will mutate on retry
        if not next_page_token:
            params["status"] = "any"
        return params

    def get_error_handler(self):
        return self._error_handler


class Disputes(IncrementalShopifyStream):
    data_field = "disputes"
    filter_field = "since_id"
    cursor_field = "id"
    order_field = "id"

    def path(self, **kwargs) -> str:
        return f"shopify_payments/{self.data_field}.json"


class MetafieldOrders(IncrementalShopifyGraphQlBulkStream):
    bulk_query: MetafieldOrder = MetafieldOrder


class DraftOrders(IncrementalShopifyStream):
    data_field = "draft_orders"


class MetafieldDraftOrders(IncrementalShopifyGraphQlBulkStream):
    bulk_query: MetafieldDraftOrder = MetafieldDraftOrder


class Products(IncrementalShopifyGraphQlBulkStream):
    bulk_query: Product = Product


class MetafieldProducts(IncrementalShopifyGraphQlBulkStream):
    parent_stream_class = Products
    bulk_query: MetafieldProduct = MetafieldProduct


class ProductImages(IncrementalShopifyGraphQlBulkStream):
    parent_stream_class = Products
    bulk_query: ProductImage = ProductImage


class MetafieldProductImages(IncrementalShopifyGraphQlBulkStream):
    parent_stream_class = Products
    bulk_query: MetafieldProductImage = MetafieldProductImage


class ProductVariants(IncrementalShopifyGraphQlBulkStream):
    bulk_query: ProductVariant = ProductVariant


class MetafieldProductVariants(IncrementalShopifyGraphQlBulkStream):
    bulk_query: MetafieldProductVariant = MetafieldProductVariant


class AbandonedCheckouts(IncrementalShopifyStream):
    data_field = "checkouts"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["status"] = "any"
        return params


class CustomCollections(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "custom_collections"
    deleted_events_api_name = "Collection"


class CustomerJourneySummary(IncrementalShopifyGraphQlBulkStream):
    bulk_query: CustomerJourney = CustomerJourney
    primary_key = "order_id"


class SmartCollections(IncrementalShopifyStream):
    data_field = "smart_collections"


class MetafieldSmartCollections(MetafieldShopifySubstream):
    parent_stream_class = SmartCollections


class Collects(IncrementalShopifyStream):
    """
    Collects stream does not support Incremental Refresh based on datetime fields, only `since_id` is supported:
    https://shopify.dev/docs/admin-api/rest/reference/products/collect

    The Collect stream is the link between Products and Collections, if the Collection is created for Products,
    the `collect` record is created, it's reasonable to Full Refresh all collects. As for Incremental refresh -
    we would use the since_id specificaly for this stream.
    """

    data_field = "collects"
    cursor_field = "id"
    order_field = "id"
    filter_field = "since_id"


class Collections(IncrementalShopifyGraphQlBulkStream):
    bulk_query: Collection = Collection


class MetafieldCollections(IncrementalShopifyGraphQlBulkStream):
    bulk_query: MetafieldCollection = MetafieldCollection


class BalanceTransactions(IncrementalShopifyStream):
    """
    PaymentsTransactions stream does not support Incremental Refresh based on datetime fields, only `since_id` is supported:
    https://shopify.dev/api/admin-rest/2021-07/resources/transactions
    """

    data_field = "transactions"
    cursor_field = "id"
    order_field = "id"
    filter_field = "since_id"

    def path(self, **kwargs) -> str:
        return f"shopify_payments/balance/{self.data_field}.json"


class OrderAgreements(IncrementalShopifyGraphQlBulkStream):
    bulk_query: OrderAgreement = OrderAgreement


class OrderRefunds(IncrementalShopifyNestedStream):
    parent_stream_class = Orders
    # override default cursor field
    cursor_field = "created_at"
    nested_entity = "refunds"


class OrderRisks(IncrementalShopifyGraphQlBulkStream):
    bulk_query: OrderRisk = OrderRisk


class Transactions(IncrementalShopifySubstream):
    parent_stream_class = Orders
    slice_key = "order_id"
    data_field = "transactions"
    cursor_field = "created_at"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class TransactionsGraphql(IncrementalShopifyGraphQlBulkStream):
    bulk_query: Transaction = Transaction
    cursor_field = "created_at"

    @property
    def name(self) -> str:
        # override default name. This stream is essentially the same as `Transactions` stream, but it's using GraphQL API, which does not include the user_id field
        return "transactions"

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        This stream has the same schema as `Transactions` stream, except of:
         - fields: [ `device_id, source_name, user_id, location_id` ]

           Specifically:
            - `user_id` field requires `Shopify Plus` / be authorised via `Financialy Embedded App`.
            - additional `read_users` scope is required https://shopify.dev/docs/api/usage/access-scopes#authenticated-access-scopes
        """
        return ResourceSchemaLoader(package_name_from_class(Transactions)).get_schema("transactions")


class TenderTransactions(IncrementalShopifyStream):
    data_field = "tender_transactions"
    cursor_field = "processed_at"
    filter_field = "processed_at_min"
    order_field = "processed_at"


class Pages(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "pages"
    deleted_events_api_name = "Page"


class MetafieldPages(MetafieldShopifySubstream):
    parent_stream_class = Pages


class PriceRules(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "price_rules"
    deleted_events_api_name = "PriceRule"


class DiscountCodes(IncrementalShopifyGraphQlBulkStream):
    bulk_query: DiscountCode = DiscountCode


class Locations(ShopifyStream):
    """
    The location API does not support any form of filtering.
    https://shopify.dev/api/admin-rest/2021-07/resources/location

    Therefore, only FULL_REFRESH mode is supported.
    """

    data_field = "locations"


class MetafieldLocations(IncrementalShopifyGraphQlBulkStream):
    bulk_query: MetafieldLocation = MetafieldLocation
    filter_field = None


class InventoryLevels(IncrementalShopifyGraphQlBulkStream):
    bulk_query: InventoryLevel = InventoryLevel


class InventoryItems(IncrementalShopifyGraphQlBulkStream):
    bulk_query: InventoryItem = InventoryItem


class FulfillmentOrders(IncrementalShopifyGraphQlBulkStream):
    bulk_query: FulfillmentOrder = FulfillmentOrder


class Fulfillments(IncrementalShopifyNestedStream):
    parent_stream_class = Orders
    nested_entity = "fulfillments"


class Shop(ShopifyStream):
    data_field = "shop"


class MetafieldShops(IncrementalShopifyStream):
    data_field = "metafields"


class CustomerAddress(IncrementalShopifyGraphQlBulkStream):
    parent_stream_class = Customers
    bulk_query: CustomerAddresses = CustomerAddresses
    cursor_field = "id"


class ProfileLocationGroups(IncrementalShopifyGraphQlBulkStream):
    bulk_query: ProfileLocationGroups = ProfileLocationGroups
    filter_field = None


class Countries(HttpSubStream, FullRefreshShopifyGraphQlBulkStream):
    # https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfiles
    _page_cursor = None
    _sub_page_cursor = None

    _synced_countries_ids = []

    query = DeliveryProfile
    response_field = "deliveryProfiles"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json().get("data", {})
        if not json_response:
            return None

        page_info = json_response.get("deliveryProfiles", {}).get("pageInfo", {})

        sub_page_info = {"hasNextPage": False}
        # only one top page in query
        delivery_profiles_nodes = json_response.get("deliveryProfiles", {}).get("nodes")
        if delivery_profiles_nodes:
            profile_location_groups = delivery_profiles_nodes[0].get("profileLocationGroups")
            if profile_location_groups:
                sub_page_info = (
                    # only first one
                    profile_location_groups[0].get("locationGroupZones", {}).get("pageInfo", {})
                )

        if not sub_page_info["hasNextPage"] and not page_info["hasNextPage"]:
            return None
        if sub_page_info["hasNextPage"]:
            # The cursor to retrieve nodes after in the connection. Typically, you should pass the endCursor of the previous page as after.
            self._sub_page_cursor = sub_page_info["endCursor"]
        if page_info["hasNextPage"] and not sub_page_info["hasNextPage"]:
            # The cursor to retrieve nodes after in the connection. Typically, you should pass the endCursor of the previous page as after.
            self._page_cursor = page_info["endCursor"]
            self._sub_page_cursor = None

        return {
            "cursor": self._page_cursor,
            "sub_cursor": self._sub_page_cursor,
        }

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        location_group_id = stream_slice["parent"]["profile_location_groups"][0]["locationGroup"]["id"]
        return {
            "query": self.query(location_group_id=location_group_id, location_group_zones_cursor=self._sub_page_cursor).get(
                query_args={
                    "cursor": self._page_cursor,
                }
            ),
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # TODO: to refactor this using functools + partial, see comment https://github.com/airbytehq/airbyte/pull/55823#discussion_r2016335672
        for node in super().parse_response(response, **kwargs):
            for location_group in node.get("profileLocationGroups", []):
                for location_group_zone in location_group.get("locationGroupZones", {}).get("nodes", []):
                    for country in location_group_zone.get("zone", {}).get("countries"):
                        country = self._process_country(country)
                        if country["id"] not in self._synced_countries_ids:
                            self._synced_countries_ids.append(country["id"])
                            yield country

    def _process_country(self, country: Mapping[str, Any]) -> Mapping[str, Any]:
        country["id"] = int(country["id"].split("/")[-1])

        for province in country.get("provinces", []):
            province["id"] = int(province["id"].split("/")[-1])
            province["country_id"] = country["id"]

        if country.get("code"):
            country["rest_of_world"] = country["code"]["rest_of_world"] if country["code"].get("rest_of_world") is not None else "*"
            country["code"] = country["code"]["country_code"] if country["code"].get("country_code") is not None else "*"

        country["shop_url"] = self.config["shop"]
        return country
