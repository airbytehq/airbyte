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

import time
import math
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode
# from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


class ShopifyStream(HttpStream, ABC):
    url_base = ""
    limit = 1

    def __init__(self, shop: str, api_key: str, api_password: str, api_version: str, **kwargs):
        super().__init__(**kwargs)
        self.shop = shop
        self.api_key = api_key
        self.api_password = api_password
        self.api_version = api_version
        # self.since_id = 0

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()[self.data_field]
        if len(decoded_response) < self.limit:
            return None
        else:
            self.since_id = decoded_response[-1]["id"]
            time.sleep(2)
            print(self.since_id)
            return {"since_id": self.since_id}

    def request_params(
            self, 
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs
        ) -> MutableMapping[str, Any]:
        # params = super().request_params(next_page_token=next_page_token, **kwargs)
            params = {"limit": self.limit}
            #params["limit"] = self.limit
            #params["since_id"] = self.since_id
            if next_page_token:
                params.update(**next_page_token)
            return params

    def parse_response(
        self, 
        response: requests.Response, 
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs
        ) -> Iterable[Mapping]:
            json_response = response.json()
            records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
            for record in records:
                yield record

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""


#class Customers(ShopifyStream):
#    cursor_field = "id"
#    primary_key = "id"
#    data_field = "customers"
#
#    def path(self, **kwargs) -> str:
#        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"
#       return f"{self.url_base}/{self.data_field}.json"    

class Orders(ShopifyStream):
    data_field = "orders"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"
    #   return f"{self.url_base}/{self.data_field}.json"

class Products(ShopifyStream):
    data_field = "products"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

class AbandonedCheckouts(ShopifyStream):
    data_field = "checkouts"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

class Metafields(ShopifyStream):
    data_field = "metafields"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

class CustomCollections(ShopifyStream):
    data_field = "custom_collections"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

class Collects(ShopifyStream):
    data_field = "collects"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

# class Transactions(ShopifyStream):
#    data_field = "transactions"
#    primary_key = "id"
#
#    def path(self, **kwargs) -> str:
#        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

# class OrderRefunds(ShopifyStream):
#    data_field = "order_refunds"
#    primary_key = "id"
#
#    def path(self, **kwargs) -> str:
#        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"

# Basic incremental stream
class IncrementalShopifyStream(ShopifyStream, ABC):

    state_checkpoint_interval = 1

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        return {self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, 0))}

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["since_id"] = stream_state.get(self.cursor_field)
        return params


class Customers(IncrementalShopifyStream):
    cursor_field = "id"
    primary_key = "id"
    data_field = "customers"

    def path(self, **kwargs) -> str:
        return f"https://{self.api_key}:{self.api_password}@{self.shop}.myshopify.com/admin/api/{self.api_version}/{self.data_field}.json"
    

class Test(IncrementalShopifyStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


# Source
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
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        # authenticator = HttpAuthenticator(config["api_key"],config["api_password"])
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
            Collects(**args)
        ]
