#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

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
        yield from records

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""


# Basic incremental stream
class IncrementalShopifyStream(ShopifyStream, ABC):

    # Setting the check point interval to the limit of the records output
    @property
    def state_checkpoint_interval(self) -> int:
        return super().limit

    # Setting the default cursor field for all streams
    cursor_field = "updated_at"

    @stream_state_cache.cache_stream_state
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

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
                if record.get(self.cursor_field) >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class Customers(IncrementalShopifyStream):
    data_field = "customers"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class OrderSubstream(IncrementalShopifyStream):
    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        # get the last saved orders stream state
        orders_stream = Orders(self.config)
        orders_stream_state = stream_state_cache.cached_state.get(orders_stream.name)
        for data in orders_stream.read_records(stream_state=orders_stream_state, **kwargs):
            slice = super().read_records(stream_slice={"order_id": data["id"]}, **kwargs)
            yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=slice)


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


class OrderRefunds(OrderSubstream):
    data_field = "refunds"
    order_field = "created_at"
    cursor_field = "created_at"
    filter_field = "created_at_min"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"


class OrderRisks(OrderSubstream):
    data_field = "risks"
    order_field = "id"
    cursor_field = "id"
    filter_field = "since_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"

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


class Transactions(OrderSubstream):
    data_field = "transactions"
    order_field = "created_at"
    cursor_field = "created_at"
    filter_field = "created_at_min"

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


class DiscountCodes(IncrementalShopifyStream):
    data_field = "discount_codes"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        price_rule_id = stream_slice["price_rule_id"]
        return f"price_rules/{price_rule_id}/{self.data_field}.json"

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        # get the last saved price_rules stream state
        price_rules_stream = PriceRules(self.config)
        price_rules_stream_state = stream_state_cache.cached_state.get(price_rules_stream.name)
        for data in price_rules_stream.read_records(stream_state=price_rules_stream_state, **kwargs):
            slice = super().read_records(stream_slice={"price_rule_id": data["id"]}, **kwargs)
            yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=slice)


class ShopifyAuthenticator(TokenAuthenticator):

    """
    Making Authenticator to be able to accept Header-Based authentication.
    """

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Shopify-Access-Token": f"{self._token}"}


# Basic Connections Check
class SourceShopify(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:

        """
        Testing connection availability for the connector.
        """
        auth = ShopifyAuthenticator(token=config["api_password"]).get_auth_header()
        api_version = "2021-07"  # Latest Stable Release

        url = f"https://{config['shop']}.myshopify.com/admin/api/{api_version}/shop.json"

        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """

        config["authenticator"] = ShopifyAuthenticator(token=config["api_password"])

        return [
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
        ]
