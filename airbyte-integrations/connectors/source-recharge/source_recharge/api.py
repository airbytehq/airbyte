#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

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
    period_in_days = 30  # Slice data request for 1 month
    raise_on_http_errors = True

    # registering the default schema transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._start_date = config["start_date"]

    @property
    def data_path(self):
        return self.name

    @property
    @abstractmethod
    def api_version(self) -> str:
        pass

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"x-recharge-version": self.api_version}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.name

    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    @abstractmethod
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        pass

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

        # dates are inclusive, so we add 1 second so that time periods do not overlap
        start_date = pendulum.parse(start_date).add(seconds=1)

        while start_date <= now:
            end_date = start_date.add(days=self.period_in_days)
            yield {"start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"), "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S")}
            start_date = end_date.add(seconds=1)


class RechargeStreamModernAPI(RechargeStream):
    api_version = "2021-11"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        cursor = response.json().get("next_cursor")
        if cursor:
            return {"cursor": cursor}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}

        # if a cursor value is passed, only limit can be passed with it!
        if next_page_token:
            params.update(next_page_token)
        else:
            params.update(
                {
                    "sort_by": "updated_at-asc",
                    "updated_at_min": (stream_slice or {}).get("start_date", self._start_date),
                    "updated_at_max": (stream_slice or {}).get("end_date", self._start_date),
                }
            )
        return params


class RechargeStreamDeprecatedAPI(RechargeStream):
    api_version = "2021-01"

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
            "sort_by": "updated_at-asc",
            "updated_at_min": (stream_slice or {}).get("start_date", self._start_date),
            "updated_at_max": (stream_slice or {}).get("end_date", self._start_date),
        }

        if next_page_token:
            params.update(next_page_token)

        return params


class IncrementalRechargeStream(RechargeStream, ABC):
    cursor_field = "updated_at"
    state_checkpoint_interval = 250

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class Addresses(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Addresses Stream: https://developer.rechargepayments.com/v1-shopify?python#list-addresses
    """


class Charges(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Charges Stream: https://developer.rechargepayments.com/v1-shopify?python#list-charges
    """


class Collections(RechargeStreamModernAPI):
    """
    Collections Stream
    """


class Customers(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Customers Stream: https://developer.rechargepayments.com/v1-shopify?python#list-customers
    """


class Discounts(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Discounts Stream: https://developer.rechargepayments.com/v1-shopify?python#list-discounts
    """


class Metafields(RechargeStreamModernAPI):
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


class Onetimes(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Onetimes Stream: https://developer.rechargepayments.com/v1-shopify?python#list-onetimes
    """


class OrdersDeprecatedApi(RechargeStreamDeprecatedAPI, IncrementalRechargeStream):
    """
    Orders Stream: https://developer.rechargepayments.com/v1-shopify?python#list-orders
    Using old API version to avoid schema changes and loosing email, first_name, last_name columns, because in new version it not present
    """

    name = "orders"


class OrdersModernApi(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Orders Stream: https://developer.rechargepayments.com/v1-shopify?python#list-orders
    Using newer API version to fetch all the data, based on the Customer's UI toggle `use_deprecated_api: FALSE`.
    """

    name = "orders"


class Products(RechargeStreamDeprecatedAPI):
    """
    Products Stream: https://developer.rechargepayments.com/v1-shopify?python#list-products
    Products endpoint has 422 error with 2021-11 API version
    """


class Shop(RechargeStreamDeprecatedAPI):
    """
    Shop Stream: https://developer.rechargepayments.com/v1-shopify?python#shop
    Shop endpoint is not available in 2021-11 API version
    """

    primary_key = ["shop", "store"]
    data_path = None

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        return [{}]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        return {}


class Subscriptions(RechargeStreamModernAPI, IncrementalRechargeStream):
    """
    Subscriptions Stream: https://developer.rechargepayments.com/v1-shopify?python#list-subscriptions
    """

    # reduce the slice date range to avoid 504 - Gateway Timeout on the Server side,
    # since this stream could contain lots of data, causing the server to timeout.
    # related issue: https://github.com/airbytehq/oncall/issues/3424
    period_in_days = 14
