from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_bold.schemas import Customer, Product, Category


class BoldStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class BoldStream(HttpStream, ABC)` which is the current class
    `class Customers(BoldStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(BoldStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalBoldStream((BoldStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://api.boldcommerce.com"

    def __init__(self, config, authenticator, **kwargs):
        super().__init__(authenticator=authenticator, **kwargs)
        self.shop_identifier = config.get("shop_identifier", "")

    @property
    @abstractmethod
    def schema(self):
        """Pydantic model that represents stream schema"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        # response_json = response.json().get("pagination", {})
        return {}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        # next_page = next_page_token or {}
        # return {**next_page_token, "authenticator": self.authenticator}
        pass

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            yield record

    def get_json_schema(self) -> Mapping[str, Any]:
        """Use Pydantic schema"""
        return self.schema.schema()


class IncrementalBoldStream(BoldStream, ABC):
    """
    Baseclass for all incremental streams of Bold source. Override cursor field property in order to use
    incremental stream.
    """
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """


    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class Customers(IncrementalBoldStream):
    """
    Docs: https://developer.boldcommerce.com/default/api/customers#tag/Customers
    """
    schema = Customer
    primary_key = "id"
    cursor_field = "created_at"

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Specifies path for customers endpoint of bold.
        """
        return f"customers/v2/shops/{self.shop_identifier}/customers"


class Products(IncrementalBoldStream):
    """
    Docs: https://developer.boldcommerce.com/default/api/products
    """
    schema = Product
    primary_key = "id"
    cursor_field = "created_at"

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"products/v2/shops/{self.shop_identifier}/products"


class Categories(IncrementalBoldStream):
    """
    Docs: https://developer.boldcommerce.com/default/api/products#tag/Categories
    """
    schema = Category
    primary_key = "id"
    cursor_field = "created_at"

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"products/v2/shops/{self.shop_identifier}/categories"
