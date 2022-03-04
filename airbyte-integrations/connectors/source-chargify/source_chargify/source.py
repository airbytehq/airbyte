#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from requests.auth import HTTPBasicAuth
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode



# Basic full refresh stream
class ChargifyStream(HttpStream, ABC):

    def __init__(self, subdomain: str, per_page: int, page: str, *args, **kwargs):
        super().__init__(**kwargs)

        self._subdomain = subdomain
        self._per_page = per_page
        self._page = page
    
    @property
    def url_base(self):
        return f"https://{self._subdomain}.chargify.com"

    @property
    def is_first_requests(self)-> bool:
        return True

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        
        results = response.json()
        if results:
            url_query = urlparse(response.url).query
            query_params = parse_qs(url_query)

            new_params = {}
            for param in query_params:
                if param == "page":
                    new_params[param] = int(query_params[param][0]) + 1
                new_params[param] = query_params[param][0]

            return new_params
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        if next_page_token is None and self.is_first_requests:
            return {"page": self._page, "per_page": self._per_page}

        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


class Customers(ChargifyStream):

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
    
        return "customers.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgyNzY-list-or-find-customers
        # it returns an Array of Customers objects.
        customers = response.json()
        for customer in customers:
            yield customer["customer"]


class Subscriptions(ChargifyStream):

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"

    def path(self, **kwargs) -> str:
    
        return "subscriptions.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgyNzY-list-or-find-customers
        # it returns an Array of Customers objects.
        subscriptions = response.json()
        for subscription in subscriptions:
            yield subscription["subscription"]


# Source
class SourceChargify(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config) -> Tuple[bool, any]:
        try:
            auth = HTTPBasicAuth(config["api_key"], "X")
            converted_args = self.convert_config2stream_args(config)
            customers_gen = Customers(authenticator=auth, **converted_args).read_records(sync_mode=SyncMode.full_refresh)
            next(customers_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Chargify API with the provided credentials - {repr(error)}"

    @classmethod
    def convert_config2stream_args(cls, config: Mapping[str, Any])-> Mapping[str, Any]:
        """Convert the input config to streams
        """

        return {"subdomain": config["subdomain"], "page": 1, "per_page": 200}

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        
        auth = HTTPBasicAuth(config["api_key"], "X")  # https://developers.chargify.com/docs/api-docs/YXBpOjE0MTA4MjYx-chargify-api-documentation
        converted_args = self.convert_config2stream_args(config)
        return [Customers(authenticator=auth, **converted_args), Subscriptions(authenticator=auth, **converted_args)]
