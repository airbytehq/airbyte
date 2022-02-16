#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .auth import ShopifyAuthenticator
from .transform import DataTypeEnforcer
from .utils import SCOPES_MAPPING
from .utils import EagerlyCachedStreamState as stream_state_cache
from .utils import ShopifyRateLimiter as limiter


class ShopifyStream(HttpStream, ABC):
    # Latest Stable Release
    api_version = "2021-07"
    # Page size
    limit = 250
    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"
    order_field = "updated_at"
    filter_field = "updated_at_min"

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self._transformer = DataTypeEnforcer(self.get_json_schema())
        self.config = config

    @property
    def url_base(self) -> str:
        return f"https://{self.config['shop']}.myshopify.com/admin/api/{self.api_version}/"

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
            params[self.filter_field] = self.config["start_date"]
        return params

    @limiter.balance_rate_limit()
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    @stream_state_cache.cache_stream_state
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["order"] = f"{self.order_field} asc"
            if stream_state:
                params[self.filter_field] = stream_state.get(self.cursor_field)
        return params

    # Parse the stream_slice with respect to stream_state for Incremental refresh
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            for record in records_slice:
                if record.get(self.cursor_field, "") >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class Customers(IncrementalShopifyStream):
    data_field = "customers"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


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


class ChildSubstream(IncrementalShopifyStream):
    """
    ChildSubstream - provides slicing functionality for streams using parts of data from parent stream.
    For example:
       - `Refunds Orders` is the entity of `Orders`,
       - `OrdersRisks` is the entity of `Orders`,
       - `DiscountCodes` is the entity of `PriceRules`, etc.

    ::  @ parent_stream_class - defines the parent stream object to read from
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

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Reading the parent stream for slices with structure:
        EXAMPLE: for given nested_record as `id` of Orders,

        Output: [ {slice_key: 123}, {slice_key: 456}, ..., {slice_key: 999} ]
        """
        parent_stream = self.parent_stream_class(self.config)
        parent_stream_state = stream_state_cache.cached_state.get(parent_stream.name)
        for record in parent_stream.read_records(stream_state=parent_stream_state, **kwargs):
            # to limit the number of API Calls and reduce the time of data fetch,
            # we can pull the ready data for child_substream, if nested data is present,
            # and corresponds to the data of child_substream we need.
            if self.nested_substream:
                if record.get(self.nested_substream):
                    yield {self.slice_key: record[self.nested_record]}
            else:
                yield {self.slice_key: record[self.nested_record]}

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


class DraftOrders(IncrementalShopifyStream):
    data_field = "draft_orders"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class Products(IncrementalShopifyStream):
    data_field = "products"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


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


class Metafields(IncrementalShopifyStream):
    data_field = "metafields"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class CustomCollections(IncrementalShopifyStream):
    data_field = "custom_collections"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token and not stream_state:
            params[self.filter_field] = 0
        return params


class OrderRefunds(ChildSubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"

    data_field = "refunds"
    cursor_field = "created_at"
    # we pull out the records that we already know has the refunds data from Orders object
    nested_substream = "refunds"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class OrderRisks(ChildSubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"

    data_field = "risks"
    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}


class Transactions(ChildSubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"

    data_field = "transactions"
    cursor_field = "created_at"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class Pages(IncrementalShopifyStream):
    data_field = "pages"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class PriceRules(IncrementalShopifyStream):
    data_field = "price_rules"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class DiscountCodes(ChildSubstream):
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


class InventoryLevels(ChildSubstream):
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


class InventoryItems(ChildSubstream):
    parent_stream_class: object = Products
    slice_key = "id"
    nested_record = "variants"
    nested_record_field_name = "inventory_item_id"
    data_field = "inventory_items"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ids = ",".join(str(x[self.nested_record_field_name]) for x in stream_slice[self.slice_key])
        return f"inventory_items.json?ids={ids}"


class FulfillmentOrders(ChildSubstream):
    parent_stream_class: object = Orders
    slice_key = "order_id"

    data_field = "fulfillment_orders"

    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice[self.slice_key]
        return f"orders/{order_id}/{self.data_field}.json"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}


class Fulfillments(ChildSubstream):
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

        always_permitted_streams = ["Metafields", "Shop"]

        permitted_streams = [
            stream
            for user_scope in user_scopes
            if user_scope["handle"] in SCOPES_MAPPING
            for stream in SCOPES_MAPPING.get(user_scope["handle"])
        ] + always_permitted_streams

        # before adding stream to stream_instances list, please add it to SCOPES_MAPPING
        stream_instances = [
            Customers(config),
            Orders(config),
            DraftOrders(config),
            Products(config),
            AbandonedCheckouts(config),
            Metafields(config),
            CustomCollections(config),
            Collects(config),
            OrderRefunds(config),
            OrderRisks(config),
            Transactions(config),
            Pages(config),
            PriceRules(config),
            DiscountCodes(config),
            Locations(config),
            InventoryItems(config),
            InventoryLevels(config),
            FulfillmentOrders(config),
            Fulfillments(config),
            Shop(config),
        ]

        return [stream_instance for stream_instance in stream_instances if self.format_name(stream_instance.name) in permitted_streams]

    @staticmethod
    def get_user_scopes(config):
        session = requests.Session()
        headers = config["authenticator"].get_auth_header()
        response = session.get(f"https://{config['shop']}.myshopify.com/admin/oauth/access_scopes.json", headers=headers).json()
        return response["access_scopes"]

    @staticmethod
    def format_name(name):
        return "".join(x.capitalize() for x in name.split("_"))
