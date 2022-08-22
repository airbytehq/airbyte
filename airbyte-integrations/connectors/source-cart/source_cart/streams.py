#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class CartStream(HttpStream, ABC):
    primary_key = "id"

    def __init__(self, start_date: str, store_name: str, end_date: str = None, **kwargs):
        self._start_date = start_date
        self._end_date = end_date
        self.store_name = store_name
        super().__init__(**kwargs)

    @property
    def url_base(self) -> str:
        return f"https://{self.store_name}/api/v1/"

    @property
    def data_field(self) -> str:
        """
        Field of the response containing data.
        By default the value self.name will be used if this property is empty or None
        """
        return None

    def path(self, **kwargs) -> str:
        return self.name

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        We dont need to check the response.status_code == 429 since this header exists only in this case.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            return float(retry_after)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()

        if response_json.get("next_page"):
            next_query_string = urllib.parse.urlsplit(response_json.get("next_page")).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Cache-Control": "no-cache", "Content-Type": "application/json"}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        result = response_json.get(self.data_field or self.name, [])
        yield from result

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"count": 1000}
        if next_page_token:
            params.update(next_page_token)
        return params


class IncrementalCartStream(CartStream, ABC):

    state_checkpoint_interval = 1000
    cursor_field = "updated_at"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        Generates a query for incremental logic

        Docs: https://developers.cart.com/docs/rest-api/docs/query_syntax.md
        """
        params = super().request_params(stream_state=stream_state, **kwargs)
        cursor_value = stream_state.get(self.cursor_field) or self._start_date
        params["sort"] = self.cursor_field
        start_date = max(cursor_value, self._start_date)
        query = f"gt:{start_date}"
        if self._end_date and self._end_date > start_date:
            query += f" AND lt:{self._end_date}"

        params[self.cursor_field] = query
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        if current_state:
            return {self.cursor_field: max(latest_state, current_state)}
        return {}


class CustomersCart(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1customers/get
    """

    data_field = "customers"

    def path(self, **kwargs) -> str:
        return self.data_field


class Orders(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1orders/get
    """


class OrderPayments(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_payments/get
    """

    data_field = "payments"


class OrderItems(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_items/get
    """

    data_field = "items"


class OrderStatuses(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/ff5ada86bc8a0-get-order-statuses
    """

    data_field = "order_statuses"


class Products(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1products/get
    """


class Addresses(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/b3A6MjMzMTc3Njc-get-addresses
    """
