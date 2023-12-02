#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from requests.exceptions import RequestException
from source_shopify.shopify_graphql.bulk.query import PARENT_KEY, Metafields
from source_shopify.shopify_graphql.graphql import get_query_products
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .base_streams import (
    IncrementalShopifyGraphQlBulkStream,
    IncrementalShopifyNestedSubstream,
    IncrementalShopifyStream,
    IncrementalShopifyStreamWithDeletedEvents,
    IncrementalShopifySubstream,
    ShopifyStream,
)


class MetafieldShopifySubstream(IncrementalShopifySubstream):
    slice_key = "id"
    data_field = "metafields"

    parent_stream_class: object = None

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        object_id = stream_slice[self.slice_key]
        return f"{self.parent_stream_class.data_field}/{object_id}/{self.data_field}.json"


class MetafieldShopifyGraphQlBulkStream(IncrementalShopifyGraphQlBulkStream):
    @property
    def bulk_query(self) -> Metafields:
        return Metafields

    @property
    def substream(self) -> bool:
        """
        Emit only Metafields-related records.
        """
        return True

    def custom_transform(self, record: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        """
        The dependent resources have `__parentId` key in record, which signifies about the parnt-to-child relation.
        To match the existing JSON Schema for `Metafields` streams we need to:
            -- move the `id` to the `owner_id` key and extract the actual `id` (INT) from the string
            -- extract the parent resosurce from the `id` and add it to the `owner_resource` field

        Input:
            { "__parentId": "gid://shopify/Order/19435458986123", "owner_type": "ORDER" }
        Output:
            { "owner_id": 19435458986123, "owner_resource: "order"}

        More info: https://shopify.dev/docs/api/usage/bulk-operations/queries#the-jsonl-data-format
        """
        # resolve parent id from `str` to `int`
        record["owner_id"] = int(re.search(r"\d+", record[PARENT_KEY]).group())
        # add `owner_resource` field
        record["owner_resource"] = self.bulk_job.tools.camel_to_snake(record[PARENT_KEY].split("/")[3])
        # remove `__parentId` from record
        record.pop(PARENT_KEY, None)
        # convert dates from ISO-8601 to RFC-3339
        record["created_at"] = self.bulk_job.tools.from_iso8601_to_rfc3339(record, "created_at")
        record["updated_at"] = self.bulk_job.tools.from_iso8601_to_rfc3339(record, "updated_at")
        yield record


class Articles(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "articles"
    cursor_field = "id"
    order_field = "id"
    filter_field = "since_id"
    deleted_events_api_name = "Article"


class MetafieldArticles(MetafieldShopifySubstream):
    parent_stream_class: object = Articles


class Blogs(IncrementalShopifyStreamWithDeletedEvents):
    cursor_field = "id"
    order_field = "id"
    data_field = "blogs"
    filter_field = "since_id"
    deleted_events_api_name = "Blog"


class MetafieldBlogs(MetafieldShopifySubstream):
    parent_stream_class: object = Blogs


class Customers(IncrementalShopifyStream):
    data_field = "customers"


class MetafieldCustomers(MetafieldShopifyGraphQlBulkStream):
    query_path = "customers"


class Orders(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "orders"
    deleted_events_api_name = "Order"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        if not next_page_token:
            params["status"] = "any"
        return params


class Disputes(IncrementalShopifyStream):
    data_field = "disputes"
    filter_field = "since_id"
    cursor_field = "id"
    order_field = "id"

    def path(self, **kwargs) -> str:
        return f"shopify_payments/{self.data_field}.json"


class MetafieldOrders(MetafieldShopifyGraphQlBulkStream):
    query_path = "orders"


class DraftOrders(IncrementalShopifyStream):
    data_field = "draft_orders"


class MetafieldDraftOrders(MetafieldShopifyGraphQlBulkStream):
    query_path = "draftOrders"


class Products(IncrementalShopifyStreamWithDeletedEvents):
    use_cache = True
    data_field = "products"
    deleted_events_api_name = "Product"


class ProductsGraphQl(IncrementalShopifyStream):
    filter_field = "updatedAt"
    cursor_field = "updatedAt"
    data_field = "graphql"
    http_method = "POST"

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        state_value = stream_state.get(self.filter_field)
        if state_value:
            filter_value = state_value
        else:
            filter_value = self.default_filter_field_value
        query = get_query_products(
            first=self.limit, filter_field=self.filter_field, filter_value=filter_value, next_page_token=next_page_token
        )
        return {"query": query}

    @staticmethod
    def next_page_token(response: requests.Response) -> Optional[Mapping[str, Any]]:
        page_info = response.json()["data"]["products"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        if has_next_page:
            return page_info["endCursor"]
        else:
            return None

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code is requests.codes.OK:
            try:
                json_response = response.json()["data"]["products"]["nodes"]
                yield from self.produce_records(json_response)
            except RequestException as e:
                self.logger.warning(f"Unexpected error in `parse_ersponse`: {e}, the actual response data: {response.text}")


class MetafieldProducts(MetafieldShopifyGraphQlBulkStream):
    query_path = "products"


class ProductImages(IncrementalShopifyNestedSubstream):
    parent_stream_class: object = Products
    nested_substream = "images"
    # add `product_id` to each nested subrecord
    mutation_map = {"product_id": "id"}


class MetafieldProductImages(MetafieldShopifyGraphQlBulkStream):
    query_path = ["products", "images"]
    sort_key = None


class ProductVariants(IncrementalShopifyNestedSubstream):
    parent_stream_class: object = Products
    nested_substream = "variants"
    # add `product_id` to each nested subrecord
    mutation_map = {"product_id": "id"}


class MetafieldProductVariants(MetafieldShopifyGraphQlBulkStream):
    query_path = "productVariants"
    sort_key = None


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


class SmartCollections(IncrementalShopifyStream):
    data_field = "smart_collections"


class MetafieldSmartCollections(MetafieldShopifySubstream):
    parent_stream_class: object = SmartCollections


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


class Collections(IncrementalShopifySubstream):
    parent_stream_class: object = Collects
    nested_record = "collection_id"
    slice_key = "collection_id"
    data_field = "collection"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        collection_id = stream_slice[self.slice_key]
        return f"collections/{collection_id}.json"


class MetafieldCollections(MetafieldShopifyGraphQlBulkStream):
    query_path = "collections"


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


class OrderRefunds(IncrementalShopifyNestedSubstream):
    parent_stream_class: object = Orders
    # override default cursor field
    cursor_field = "created_at"
    nested_substream = "refunds"


class OrderRisks(IncrementalShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "risks"
    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class Transactions(IncrementalShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "transactions"
    cursor_field = "created_at"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class TenderTransactions(IncrementalShopifyStream):
    data_field = "tender_transactions"
    cursor_field = "processed_at"
    filter_field = "processed_at_min"


class Pages(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "pages"
    deleted_events_api_name = "Page"


class MetafieldPages(MetafieldShopifySubstream):
    parent_stream_class: object = Pages


class PriceRules(IncrementalShopifyStreamWithDeletedEvents):
    data_field = "price_rules"
    deleted_events_api_name = "PriceRule"


class DiscountCodes(IncrementalShopifySubstream):
    parent_stream_class: object = PriceRules
    slice_key = "price_rule_id"
    data_field = "discount_codes"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        price_rule_id = stream_slice["price_rule_id"]
        return f"price_rules/{price_rule_id}/{self.data_field}.json"


class Locations(ShopifyStream):
    """
    The location API does not support any form of filtering.
    https://shopify.dev/api/admin-rest/2021-07/resources/location

    Therefore, only FULL_REFRESH mode is supported.
    """

    data_field = "locations"


class MetafieldLocations(MetafieldShopifyGraphQlBulkStream):
    query_path = "locations"
    filter_field = None
    sort_key = None


class InventoryLevels(IncrementalShopifySubstream):
    parent_stream_class: object = Locations
    slice_key = "location_id"
    data_field = "inventory_levels"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        location_id = stream_slice["location_id"]
        return f"locations/{location_id}/{self.data_field}.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records_stream = super().parse_response(response, **kwargs)

        def generate_key(record):
            record.update({"id": "|".join((str(record.get("location_id", "")), str(record.get("inventory_item_id", ""))))})
            return record

        # associate the surrogate key
        yield from map(generate_key, records_stream)


class InventoryItems(IncrementalShopifySubstream):
    parent_stream_class: object = Products
    slice_key = "id"
    nested_record = "variants"
    nested_record_field_name = "inventory_item_id"
    data_field = "inventory_items"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ids = ",".join(str(x[self.nested_record_field_name]) for x in stream_slice[self.slice_key])
        return f"inventory_items.json?ids={ids}"


class FulfillmentOrders(IncrementalShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "fulfillment_orders"
    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice[self.slice_key]
        return f"orders/{order_id}/{self.data_field}.json"


class Fulfillments(IncrementalShopifyNestedSubstream):
    parent_stream_class: object = Orders
    nested_substream = "fulfillments"


class Shop(ShopifyStream):
    data_field = "shop"


class MetafieldShops(IncrementalShopifyStream):
    data_field = "metafields"


class CustomerSavedSearch(IncrementalShopifyStream):
    api_version = "2022-01"
    cursor_field = "id"
    order_field = "id"
    data_field = "customer_saved_searches"
    filter_field = "since_id"


class CustomerAddress(IncrementalShopifyNestedSubstream):
    """
    https://shopify.dev/docs/api/admin-rest/2023-10/resources/customer#resource-object
    """

    parent_stream_class: object = Customers
    cursor_field = "id"
    nested_substream = "addresses"


class Countries(ShopifyStream):
    data_field = "countries"
