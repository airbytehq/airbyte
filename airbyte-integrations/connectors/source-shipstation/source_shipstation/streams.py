from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.streams.http import HttpStream


class ShipstationStream(HttpStream, ABC):
    url_base = "https://ssapi.shipstation.com"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        json_response = response.json()
        total_pages = json_response['pages']
        current_page = json_response['page']
        if current_page < total_pages:
            return {'next_page_num': current_page + 1}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        params = {'pageSize': 500}

        if next_page_token:
            params.update({'page': next_page_token['next_page_num']})

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield {}


class Customers(ShipstationStream):
    primary_key = "customerId"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/customers"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()['customers']


class Fulfillments(ShipstationStream):
    primary_key = "fulfillmentId"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/fulfillments"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()['fulfillments']


class Products(ShipstationStream):
    primary_key = "productId"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/products"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()['products']


class Orders(ShipstationStream):
    primary_key = "orderId"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/orders"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()['orders']


class Stores(ShipstationStream):
    primary_key = "storeId"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/stores"


class Warehouses(ShipstationStream):
    primary_key = "warehouseId"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/warehouses"


class IncrementalShipstationStream(ShipstationStream, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class Employees(IncrementalShipstationStream):

    cursor_field = "start_date"
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
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

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()
