#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class RechargeStream(HttpStream, ABC):
    primary_key = "id"
    url_base = "https://api.rechargeapps.com/"

    limit = 250
    page_num = 1
    period_in_months = 1  # Slice data request for 1 month
    raise_on_http_errors = True

    # regestring the default schema transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._start_date = config["start_date"]

    @property
    def data_path(self):
        return self.name

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = self.get_stream_data(response.json())
        if len(stream_data) == self.limit:
            self.page_num += 1
            return {"page": self.page_num}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {
            "limit": self.limit,
            "updated_at_min": (stream_slice or {}).get("start_date", self._start_date),
            "updated_at_max": (stream_slice or {}).get("end_date", self._start_date),
        }

        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        stream_data = self.get_stream_data(response_data)

        yield from stream_data

    def get_stream_data(self, response_data: Any) -> List[dict]:
        if self.data_path:
            return response_data.get(self.data_path, [])
        else:
            return [response_data]

    def should_retry(self, response: requests.Response) -> bool:
        content_length = int(response.headers.get("Content-Length", 0))
        incomplete_data_response = response.status_code == 200 and content_length > len(response.content)

        if incomplete_data_response:
            return True

        return super().should_retry(response)

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = (stream_state or {}).get(self.cursor_field, self._start_date) if self.cursor_field else self._start_date

        now = pendulum.now()

        start_date = pendulum.parse(start_date)

        while start_date <= now:
            end_date = start_date.add(months=self.period_in_months)
            yield {"start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"), "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S")}
            start_date = end_date


class IncrementalRechargeStream(RechargeStream, ABC):
    cursor_field = "updated_at"

    @property
    def state_checkpoint_interval(self):
        return self.limit

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class Addresses(IncrementalRechargeStream):
    """
    Addresses Stream: https://developer.rechargepayments.com/v1-shopify?python#list-addresses
    """


class Charges(IncrementalRechargeStream):
    """
    Charges Stream: https://developer.rechargepayments.com/v1-shopify?python#list-charges
    """


class Collections(RechargeStream):
    """
    Collections Stream
    """


class Customers(IncrementalRechargeStream):
    """
    Customers Stream: https://developer.rechargepayments.com/v1-shopify?python#list-customers
    """


class Discounts(IncrementalRechargeStream):
    """
    Discounts Stream: https://developer.rechargepayments.com/v1-shopify?python#list-discounts
    """


class Metafields(RechargeStream):
    """
    Metafields Stream: https://developer.rechargepayments.com/v1-shopify?python#list-metafields
    """

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit, "owner_resource": (stream_slice or {}).get("owner_resource")}
        if next_page_token:
            params.update(next_page_token)

        return params

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        owner_resources = ["customer", "store", "subscription"]
        yield from [{"owner_resource": owner} for owner in owner_resources]


class Onetimes(IncrementalRechargeStream):
    """
    Onetimes Stream: https://developer.rechargepayments.com/v1-shopify?python#list-onetimes
    """


class Orders(IncrementalRechargeStream):
    """
    Orders Stream: https://developer.rechargepayments.com/v1-shopify?python#list-orders
    """


class Products(RechargeStream):
    """
    Products Stream: https://developer.rechargepayments.com/v1-shopify?python#list-products
    """


class Shop(RechargeStream):
    """
    Shop Stream: https://developer.rechargepayments.com/v1-shopify?python#shop
    """

    primary_key = ["shop", "store"]
    data_path = None


class Subscriptions(IncrementalRechargeStream):
    """
    Subscriptions Stream: https://developer.rechargepayments.com/v1-shopify?python#list-subscriptions
    """
