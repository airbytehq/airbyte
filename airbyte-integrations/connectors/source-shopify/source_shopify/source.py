#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from requests.exceptions import RequestException

from .auth import ShopifyAuthenticator
from .graphql import get_query_products
from .transform import DataTypeEnforcer
from .utils import SCOPES_MAPPING, ApiTypeEnum
from .utils import EagerlyCachedStreamState as stream_state_cache
from .utils import ErrorAccessScopes
from .utils import ShopifyRateLimiter as limiter


class ShopifyStream(HttpStream, ABC):
    # Latest Stable Release
    api_version = "2022-10"
    # Page size
    limit = 250
    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"
    order_field = "updated_at"
    filter_field = "updated_at_min"

    raise_on_http_errors = True

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self._transformer = DataTypeEnforcer(self.get_json_schema())
        self.config = config

    @property
    def url_base(self) -> str:
        return f"https://{self.config['shop']}.myshopify.com/admin/api/{self.api_version}/"

    @property
    def default_filter_field_value(self) -> Union[int, str]:
        # certain streams are using `since_id` field as `filter_field`, which requires to use `int` type,
        # but many other use `str` values for this, we determine what to use based on `filter_field` value
        # by default, we use the user defined `Start Date` as initial value, or 0 for `id`-dependent streams.
        return 0 if self.filter_field == "since_id" else self.config["start_date"]

    @staticmethod
    def next_page_token(response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        else:
            params["order"] = f"{self.order_field} asc"
            params[self.filter_field] = self.default_filter_field_value
        return params

    @limiter.balance_rate_limit()
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code is requests.codes.OK:
            try:
                json_response = response.json()
                records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
                yield from self.produce_records(records)
            except RequestException as e:
                self.logger.warn(f"Unexpected error in `parse_ersponse`: {e}, the actual response data: {response.text}")
                yield {}

    def produce_records(self, records: Union[Iterable[Mapping[str, Any]], Mapping[str, Any]] = None) -> Iterable[Mapping[str, Any]]:
        # transform method was implemented according to issue 4841
        # Shopify API returns price fields as a string and it should be converted to number
        # this solution designed to convert string into number, but in future can be modified for general purpose
        if isinstance(records, dict):
            # for cases when we have a single record as dict
            # add shop_url to the record to make querying easy
            records["shop_url"] = self.config["shop"]
            yield self._transformer.transform(records)
        else:
            # for other cases
            for record in records:
                # add shop_url to the record to make querying easy
                record["shop_url"] = self.config["shop"]
                yield self._transformer.transform(record)

    def should_retry(self, response: requests.Response) -> bool:
        error_mapping = {
            404: f"Stream `{self.name}` - not available or missing, skipping...",
            403: f"Stream `{self.name}` - insufficient permissions, skipping...",
            # extend the mapping with more handable errors, if needed.
        }
        status = response.status_code
        if status in error_mapping.keys():
            setattr(self, "raise_on_http_errors", False)
            self.logger.warn(error_mapping.get(status))
            return False
        else:
            return super().should_retry(response)

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""


class IncrementalShopifyStream(ShopifyStream, ABC):

    # Setting the check point interval to the limit of the records output
    @property
    def state_checkpoint_interval(self) -> int:
        return super().limit

    # Setting the default cursor field for all streams
    cursor_field = "updated_at"

    @property
    def default_state_comparison_value(self) -> Union[int, str]:
        # certain streams are using `id` field as `cursor_field`, which requires to use `int` type,
        # but many other use `str` values for this, we determine what to use based on `cursor_field` value
        return 0 if self.cursor_field == "id" else ""

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        last_record_value = latest_record.get(self.cursor_field) or self.default_state_comparison_value
        current_state_value = current_stream_state.get(self.cursor_field) or self.default_state_comparison_value
        return {self.cursor_field: max(last_record_value, current_state_value)}

    @stream_state_cache.cache_stream_state
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["order"] = f"{self.order_field} asc"
            if stream_state:
                params[self.filter_field] = stream_state.get(self.cursor_field)
        return params

    # Parse the `stream_slice` with respect to `stream_state` for `Incremental refresh`
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Iterable[Mapping] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            state_value = stream_state.get(self.cursor_field)
            for record in records_slice:
                if self.cursor_field in record:
                    record_value = record.get(self.cursor_field, self.default_state_comparison_value)
                    if record_value:
                        if record_value >= state_value:
                            yield record
                    else:
                        # old entities could have cursor field in place, but set to null
                        self.logger.warn(
                            f"Stream `{self.name}`, Record ID: `{record.get(self.primary_key)}` cursor value is: {record_value}, record is emitted without state comparison"
                        )
                        yield record
                else:
                    # old entities could miss the cursor field
                    self.logger.warn(
                        f"Stream `{self.name}`, Record ID: `{record.get(self.primary_key)}` missing cursor field: {self.cursor_field}, record is emitted without state comparison"
                    )
                    yield record
        else:
            yield from records_slice


class ShopifySubstream(IncrementalShopifyStream):
    """
    ShopifySubstream - provides slicing functionality for streams using parts of data from parent stream.
    For example:
       - `Refunds Orders` is the entity of `Orders`,
       - `OrdersRisks` is the entity of `Orders`,
       - `DiscountCodes` is the entity of `PriceRules`, etc.

    ::  @ parent_stream - defines the parent stream object to read from
    ::  @ slice_key - defines the name of the property in stream slices dict.
    ::  @ nested_record - the name of the field inside of parent stream record. Default is `id`.
    ::  @ nested_record_field_name - the name of the field inside of nested_record.
    ::  @ nested_substream - the name of the nested entity inside of parent stream, helps to reduce the number of
          API Calls, if present, see `OrderRefunds` stream for more.
    """

    parent_stream_class: object = None
    slice_key: str = None
    nested_record: str = "id"
    nested_record_field_name: str = None
    nested_substream = None
    nested_substream_list_field_id = None

    @cached_property
    def parent_stream(self) -> object:
        """
        Returns the instance of parent stream, if the substream has a `parent_stream_class` dependency.
        """
        return self.parent_stream_class(self.config) if self.parent_stream_class else None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """UPDATING THE STATE OBJECT:
        Stream: Transactions
        Parent Stream: Orders
        Returns:
            {
                {...},
                "transactions": {
                    "created_at": "2022-03-03T03:47:45-08:00",
                    "orders": {
                        "updated_at": "2022-03-03T03:47:46-08:00"
                    }
                },
                {...},
            }
        """
        updated_state = super().get_updated_state(current_stream_state, latest_record)
        # add parent_stream_state to `updated_state`
        updated_state[self.parent_stream.name] = stream_state_cache.cached_state.get(self.parent_stream.name)
        return updated_state

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Reading the parent stream for slices with structure:
        EXAMPLE: for given nested_record as `id` of Orders,

        Outputs:
            [
                {slice_key: 123},
                {slice_key: 456},
                {...},
                {slice_key: 999
            ]
        """
        sorted_substream_slices = []

        # reading parent nested stream_state from child stream state
        parent_stream_state = stream_state.get(self.parent_stream.name) if stream_state else {}

        # reading the parent stream
        for record in self.parent_stream.read_records(stream_state=parent_stream_state, **kwargs):
            # updating the `stream_state` with the state of it's parent stream
            # to have the child stream sync independently from the parent stream
            stream_state_cache.cached_state[self.parent_stream.name] = self.parent_stream.get_updated_state({}, record)
            # to limit the number of API Calls and reduce the time of data fetch,
            # we can pull the ready data for child_substream, if nested data is present,
            # and corresponds to the data of child_substream we need.
            if self.nested_substream and self.nested_substream_list_field_id:
                if record.get(self.nested_substream):
                    sorted_substream_slices.extend(
                        [
                            {
                                self.slice_key: sub_record[self.nested_substream_list_field_id],
                                self.cursor_field: record[self.nested_substream][0].get(
                                    self.cursor_field, self.default_state_comparison_value
                                ),
                            }
                            for sub_record in record[self.nested_record]
                        ]
                    )
            elif self.nested_substream:
                if record.get(self.nested_substream):
                    sorted_substream_slices.append(
                        {
                            self.slice_key: record[self.nested_record],
                            self.cursor_field: record[self.nested_substream][0].get(self.cursor_field, self.default_state_comparison_value),
                        }
                    )
            else:
                yield {self.slice_key: record[self.nested_record]}

        # output slice from sorted list to avoid filtering older records
        if self.nested_substream:
            if len(sorted_substream_slices) > 0:
                # sort by cursor_field
                sorted_substream_slices.sort(key=lambda x: x.get(self.cursor_field))
                for sorted_slice in sorted_substream_slices:
                    yield {self.slice_key: sorted_slice[self.slice_key]}

    def read_records(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """Reading child streams records for each `id`"""

        slice_data = stream_slice.get(self.slice_key)
        # sometimes the stream_slice.get(self.slice_key) has the list of records,
        # to avoid data exposition inside the logs, we should get the data we need correctly out of stream_slice.
        if isinstance(slice_data, list) and self.nested_record_field_name is not None and len(slice_data) > 0:
            slice_data = slice_data[0].get(self.nested_record_field_name)

        self.logger.info(f"Reading {self.name} for {self.slice_key}: {slice_data}")
        records = super().read_records(stream_slice=stream_slice, **kwargs)
        yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=records)


class MetafieldShopifySubstream(ShopifySubstream):
    slice_key = "id"
    data_field = "metafields"

    parent_stream_class: object = None

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        object_id = stream_slice[self.slice_key]
        return f"{self.parent_stream_class.data_field}/{object_id}/{self.data_field}.json"


class Articles(IncrementalShopifyStream):
    data_field = "articles"
    cursor_field = "id"
    order_field = "id"
    filter_field = "since_id"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class MetafieldArticles(MetafieldShopifySubstream):
    parent_stream_class: object = Articles


class Blogs(IncrementalShopifyStream):
    cursor_field = "id"
    order_field = "id"
    data_field = "blogs"
    filter_field = "since_id"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class MetafieldBlogs(MetafieldShopifySubstream):
    parent_stream_class: object = Blogs


class Customers(IncrementalShopifyStream):
    data_field = "customers"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class MetafieldCustomers(MetafieldShopifySubstream):
    parent_stream_class: object = Customers


class Orders(IncrementalShopifyStream):
    data_field = "orders"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        if not next_page_token:
            params["status"] = "any"
        return params


class MetafieldOrders(MetafieldShopifySubstream):
    parent_stream_class: object = Orders


class DraftOrders(IncrementalShopifyStream):
    data_field = "draft_orders"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class MetafieldDraftOrders(MetafieldShopifySubstream):
    parent_stream_class: object = DraftOrders


class Products(IncrementalShopifyStream):
    use_cache = True
    data_field = "products"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class ProductsGraphQl(IncrementalShopifyStream):
    filter_field = "updatedAt"
    cursor_field = "updatedAt"
    data_field = "graphql"
    http_method = "POST"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

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
                self.logger.warn(f"Unexpected error in `parse_ersponse`: {e}, the actual response data: {response.text}")
                yield {}


class MetafieldProducts(MetafieldShopifySubstream):
    parent_stream_class: object = Products


class ProductImages(ShopifySubstream):
    parent_stream_class: object = Products
    cursor_field = "id"
    slice_key = "product_id"
    data_field = "images"
    nested_substream = "images"
    filter_field = "since_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        product_id = stream_slice[self.slice_key]
        return f"products/{product_id}/{self.data_field}.json"


class MetafieldProductImages(MetafieldShopifySubstream):
    parent_stream_class: object = Products
    nested_record = "images"
    slice_key = "images"
    nested_substream = "images"
    nested_substream_list_field_id = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        image_id = stream_slice[self.slice_key]
        return f"product_images/{image_id}/{self.data_field}.json"


class ProductVariants(ShopifySubstream):
    parent_stream_class: object = Products
    cursor_field = "id"
    slice_key = "product_id"
    data_field = "variants"
    nested_substream = "variants"
    filter_field = "since_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        product_id = stream_slice[self.slice_key]
        return f"products/{product_id}/{self.data_field}.json"


class MetafieldProductVariants(MetafieldShopifySubstream):
    parent_stream_class: object = Products
    nested_record = "variants"
    slice_key = "variants"
    nested_substream = "variants"
    nested_substream_list_field_id = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        variant_id = stream_slice[self.slice_key]
        return f"variants/{variant_id}/{self.data_field}.json"


class AbandonedCheckouts(IncrementalShopifyStream):
    data_field = "checkouts"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["status"] = "any"
        return params


class CustomCollections(IncrementalShopifyStream):
    data_field = "custom_collections"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class SmartCollections(IncrementalShopifyStream):
    data_field = "smart_collections"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


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

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class Collections(ShopifySubstream):
    parent_stream_class: object = Collects
    nested_record = "collection_id"
    slice_key = "collection_id"
    data_field = "collection"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        collection_id = stream_slice[self.slice_key]
        return f"collections/{collection_id}.json"


class MetafieldCollections(MetafieldShopifySubstream):
    parent_stream_class: object = Collects
    slice_key = "collection_id"
    nested_record = "collection_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        object_id = stream_slice[self.slice_key]
        return f"collections/{object_id}/{self.data_field}.json"


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


class OrderRefunds(ShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "refunds"
    cursor_field = "created_at"
    # we pull out the records that we already know has the refunds data from Orders object
    nested_substream = "refunds"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class OrderRisks(ShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "risks"
    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class Transactions(ShopifySubstream):
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

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class Pages(IncrementalShopifyStream):
    data_field = "pages"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class MetafieldPages(MetafieldShopifySubstream):
    parent_stream_class: object = Pages


class PriceRules(IncrementalShopifyStream):
    data_field = "price_rules"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class DiscountCodes(ShopifySubstream):
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

    def path(self, **kwargs):
        return f"{self.data_field}.json"


class MetafieldLocations(MetafieldShopifySubstream):
    parent_stream_class: object = Locations


class InventoryLevels(ShopifySubstream):
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


class InventoryItems(ShopifySubstream):
    parent_stream_class: object = Products
    slice_key = "id"
    nested_record = "variants"
    nested_record_field_name = "inventory_item_id"
    data_field = "inventory_items"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ids = ",".join(str(x[self.nested_record_field_name]) for x in stream_slice[self.slice_key])
        return f"inventory_items.json?ids={ids}"


class FulfillmentOrders(ShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "fulfillment_orders"
    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice[self.slice_key]
        return f"orders/{order_id}/{self.data_field}.json"


class Fulfillments(ShopifySubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"
    data_field = "fulfillments"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice[self.slice_key]
        return f"orders/{order_id}/{self.data_field}.json"


class Shop(ShopifyStream):
    data_field = "shop"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class MetafieldShops(IncrementalShopifyStream):
    data_field = "metafields"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class SourceShopify(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector.
        """
        config["authenticator"] = ShopifyAuthenticator(config)
        try:
            response = list(Shop(config).read_records(sync_mode=None))
            # check for the shop_id is present in the response
            shop_id = response[0].get("id")
            if shop_id is not None:
                return True, None
        except (requests.exceptions.RequestException, IndexError) as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """
        config["authenticator"] = ShopifyAuthenticator(config)
        user_scopes = self.get_user_scopes(config)
        always_permitted_streams = ["MetafieldShops", "Shop"]
        permitted_streams = [
            stream
            for user_scope in user_scopes
            if user_scope["handle"] in SCOPES_MAPPING
            for stream in SCOPES_MAPPING.get(user_scope["handle"])
        ] + always_permitted_streams

        # before adding stream to stream_instances list, please add it to SCOPES_MAPPING
        stream_instances = [
            AbandonedCheckouts(config),
            Articles(config),
            BalanceTransactions(config),
            Blogs(config),
            Collections(config),
            Collects(config),
            CustomCollections(config),
            Customers(config),
            DiscountCodes(config),
            DraftOrders(config),
            FulfillmentOrders(config),
            Fulfillments(config),
            InventoryItems(config),
            InventoryLevels(config),
            Locations(config),
            MetafieldArticles(config),
            MetafieldBlogs(config),
            MetafieldCollections(config),
            MetafieldCustomers(config),
            MetafieldDraftOrders(config),
            MetafieldLocations(config),
            MetafieldOrders(config),
            MetafieldPages(config),
            MetafieldProductImages(config),
            MetafieldProducts(config),
            MetafieldProductVariants(config),
            MetafieldShops(config),
            MetafieldSmartCollections(config),
            OrderRefunds(config),
            OrderRisks(config),
            Orders(config),
            Pages(config),
            PriceRules(config),
            ProductImages(config),
            Products(config),
            ProductsGraphQl(config),
            ProductVariants(config),
            Shop(config),
            SmartCollections(config),
            TenderTransactions(config),
            Transactions(config),
        ]

        return [stream_instance for stream_instance in stream_instances if self.format_name(stream_instance.name) in permitted_streams]

    @staticmethod
    def get_user_scopes(config):
        session = requests.Session()
        url = f"https://{config['shop']}.myshopify.com/admin/oauth/access_scopes.json"
        headers = config["authenticator"].get_auth_header()
        response = session.get(url, headers=headers).json()
        access_scopes = response.get("access_scopes")
        if access_scopes:
            return access_scopes
        else:
            raise ErrorAccessScopes(f"Reason: {response}")

    @staticmethod
    def format_name(name):
        return "".join(x.capitalize() for x in name.split("_"))
