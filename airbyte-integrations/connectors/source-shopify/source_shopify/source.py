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
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


class ShopifyStream(HttpStream, ABC):

    # Latest Stable Release
    api_version = "2021-04"
    # Page size
    limit = 250
    # Define primary key to all streams as primary key, sort key
    primary_key = "id"

    def __init__(self, shop: str, start_date: str, api_password: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.shop = shop
        self.api_password = api_password
        self.since_id = 0

    @property
    def url_base(self) -> str:
        return f"https://{self.shop}.myshopify.com/admin/api/{self.api_version}/"

    @staticmethod
    def next_page_token(response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Getting next page link
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            params = {"limit": self.limit, **next_page_token}
        else:
            params = {"limit": self.limit, "order": f"{self.primary_key} asc", "created_at_min": self.start_date}
        return params

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

    # Getting page size as 'limit' from parrent class
    @property
    def limit(self):
        return super().limit

    state_checkpoint_interval = limit

    cursor_field = "id"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["since_id"] = stream_state.get(self.cursor_field)
        return params


class Customers(IncrementalShopifyStream):
    data_field = "customers"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class Orders(IncrementalShopifyStream):
    data_field = "orders"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def request_params(self, stream_state=None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        if next_page_token:
            params = {"limit": self.limit, **next_page_token}
        else:
            params = {
                "limit": self.limit,
                "order": f"{self.primary_key} asc",
                "created_at_min": self.start_date,
                "status": "any",
                # Add state parameter "since_id" for incremental refresh
                "since_id": stream_state.get(self.cursor_field),
            }
        return params


class Products(IncrementalShopifyStream):
    data_field = "products"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class AbandonedCheckouts(IncrementalShopifyStream):
    data_field = "checkouts"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def request_params(self, stream_state=None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        if next_page_token:
            params = {"limit": self.limit, **next_page_token}
        else:
            params = {
                "limit": self.limit,
                "order": f"{self.primary_key} asc",
                "created_at_min": self.start_date,
                "status": "any",
                # Add state parameter "since_id" for incremental refresh
                "since_id": stream_state.get(self.cursor_field),
            }
        return params


class Metafields(IncrementalShopifyStream):
    data_field = "metafields"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def request_params(self, stream_state=None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        if next_page_token:
            params = {"limit": self.limit, **next_page_token}
        else:
            params = {"limit": self.limit, "since_id": stream_state.get(self.cursor_field)}
        return params


class CustomCollections(IncrementalShopifyStream):
    data_field = "custom_collections"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"


class Collects(IncrementalShopifyStream):
    data_field = "collects"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def request_params(self, stream_state=None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        if next_page_token:
            params = {"limit": self.limit, **next_page_token}
        else:
            params = {"limit": self.limit, "since_id": stream_state.get(self.cursor_field)}
        return params


class OrderRefunds(IncrementalShopifyStream):
    data_field = "refunds"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        orders_stream = Orders(authenticator=self.authenticator, shop=self.shop, start_date=self.start_date, api_password=self.api_password)
        for data in orders_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"order_id": data["id"]}, **kwargs)


class OrderRisks(IncrementalShopifyStream):
    data_field = "risks"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        orders_stream = Orders(authenticator=self.authenticator, shop=self.shop, start_date=self.start_date, api_password=self.api_password)
        for data in orders_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"order_id": data["id"]}, **kwargs)


class Transactions(IncrementalShopifyStream):
    data_field = "transactions"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice["order_id"]
        return f"orders/{order_id}/{self.data_field}.json"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        orders_stream = Orders(authenticator=self.authenticator, shop=self.shop, start_date=self.start_date, api_password=self.api_password)
        for data in orders_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"order_id": data["id"]}, **kwargs)


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

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        price_rules_stream = PriceRules(
            authenticator=self.authenticator, shop=self.shop, start_date=self.start_date, api_password=self.api_password
        )
        for data in price_rules_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"price_rule_id": data["id"]}, **kwargs)


class ShopifyAuthenticator(HttpAuthenticator):

    """
    Making Authenticator to be able to accept Header-Based authentication.
    """

    def __init__(self, token: str):
        self.token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Shopify-Access-Token": f"{self.token}"}


# Basic Connections Check
class SourceShopify(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:

        """
        Testing connection availability for the connector.
        """

        shop = config["shop"]
        api_pass = config["api_password"]
        api_version = "2021-04"  # Latest Stable Release

        headers = {"X-Shopify-Access-Token": api_pass}
        url = f"https://{shop}.myshopify.com/admin/api/{api_version}/shop.json"

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """

        auth = ShopifyAuthenticator(token=config["api_password"])
        args = {"authenticator": auth, "shop": config["shop"], "start_date": config["start_date"], "api_password": config["api_password"]}
        return [
            Customers(**args),
            Orders(**args),
            Products(**args),
            AbandonedCheckouts(**args),
            Metafields(**args),
            CustomCollections(**args),
            Collects(**args),
            OrderRefunds(**args),
            OrderRisks(**args),
            Transactions(**args),
            Pages(**args),
            PriceRules(**args),
            DiscountCodes(**args),
        ]
