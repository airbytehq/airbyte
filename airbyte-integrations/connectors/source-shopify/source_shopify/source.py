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

# import time
import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode


class ShopifyStream(HttpStream, ABC):
    
    primary_key = "id"
    limit = 200

    def __init__(self, shop: str, api_key: str, api_password: str, api_version: str, **kwargs):
        super().__init__(**kwargs)
        self.shop = shop
        self.api_key = api_key
        self.api_password = api_password
        self.api_version = api_version
        self.since_id = 0

    @property
    def url_base(self) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if len(decoded_response.get(self.data_field)) < self.limit:
            return None
        else:
            self.since_id = decoded_response.get(self.data_field)[-1]["id"]
            # UNCOMMENT FOR DEBUG ONLY
            # print(f"\nSINCE_ID TOKEN: {self.since_id}\n")
            # time.sleep(5)
            return {"since_id": self.since_id}

    def request_params(
            self,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs
        ) -> MutableMapping[str, Any]:
            params = super().request_params(next_page_token=next_page_token, **kwargs)
            params["limit"] = self.limit
            params["since_id"] = self.since_id
            if next_page_token:
                params.update(**next_page_token)
            return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
        for record in records:
            yield record

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""


# Basic incremental stream
class IncrementalShopifyStream(ShopifyStream, ABC):
    state_checkpoint_interval = math.inf

    @property
    def cursor_field(self) -> str:
        return "id"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}

### STREAM: customers
class Customers(IncrementalShopifyStream):
    data_field = "customers"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: orders
class Orders(IncrementalShopifyStream):
    data_field = "orders"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: products
class Products(IncrementalShopifyStream):
    data_field = "products"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: abandoned_checkouts > checkouts
class AbandonedCheckouts(IncrementalShopifyStream):
    data_field = "checkouts"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: metafields
class Metafields(IncrementalShopifyStream):
    data_field = "metafields"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: custom_collections > custom collections
class CustomCollections(IncrementalShopifyStream):
    data_field = "custom_collections"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: collects
class Collects(IncrementalShopifyStream):
    data_field = "collects"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

### STREAM: Refunds from orders
class OrderRefunds(IncrementalShopifyStream):
    data_field = "refunds"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice['order_id']
        return f"orders/{order_id}/{self.data_field}.json"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        orders_stream = Orders(self.shop, self.api_key, self.api_password, self.api_version)
        for data in orders_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"order_id": data["id"]}, **kwargs)

### STREAM: Refunds from orders
class Transactions(IncrementalShopifyStream):
    data_field = "transactions"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        order_id = stream_slice['order_id']
        return f"orders/{order_id}/{self.data_field}.json"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        orders_stream = Orders(self.shop, self.api_key, self.api_password, self.api_version)
        for data in orders_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"order_id": data["id"]}, **kwargs)


# Basic Abstraction to check the connection
class SourceShopify(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # mapping config from config.json
        shop = config["shop"]
        api_key = config["api_key"]
        api_pass = config["api_password"]
        api_version = config["api_version"]  # Latest is '2021-04'

        # Construct base url for checking connetion
        url = f"https://{api_key}:{api_pass}@{shop}.myshopify.com/admin/api/{api_version}/shop.json"
        # try to connect
        try:
            session = requests.get(url)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        """
        args = {
            "shop": config["shop"],
            "api_key": config["api_key"],
            "api_password": config["api_password"],
            "api_version": config["api_version"],
        }
        return [
            Customers(**args),
            Orders(**args),
            Products(**args),
            AbandonedCheckouts(**args),
            Metafields(**args),
            CustomCollections(**args),
            Collects(**args),
            OrderRefunds(**args),
            Transactions(**args)
        ]
