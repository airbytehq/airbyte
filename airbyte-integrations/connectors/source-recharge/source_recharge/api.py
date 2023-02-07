#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class RechargeStream(HttpStream, ABC):

    primary_key = "id"
    url_base = "https://api.rechargeapps.com/"

    limit = 250
    page_num = 1
    raise_on_http_errors = True

    # regestring the default schema transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def data_path(self):
        return self.name

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

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
        params = {"limit": self.limit}
        if next_page_token:
            params.update(next_page_token)
        if stream_slice:
            params.update(stream_slice)
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
        elif response.status_code == requests.codes.FORBIDDEN:
            setattr(self, "raise_on_http_errors", False)
            self.logger.error(f"Skiping stream {self.name} because of a 403 error.")
            return False

        return super().should_retry(response)


class IncrementalRechargeStream(RechargeStream, ABC):

    cursor_field = "updated_at"

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)

    @property
    def state_checkpoint_interval(self):
        return self.limit

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        start_datetime = self._start_date
        if stream_state.get(self.cursor_field):
            start_datetime = pendulum.parse(stream_state[self.cursor_field])

        params.update({f"{self.cursor_field}_min": start_datetime.strftime("%Y-%m-%d %H:%M:%S")})
        return params


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

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        owner_resources = ["customer", "store", "subscription"]
        for owner in owner_resources:
            yield from super().read_records(stream_slice={"owner_resource": owner}, **kwargs)


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
