#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from enum import Enum
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests

from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_recharge.components.recharge_error_handler import RechargeErrorHandler


class ApiVersion(Enum):
    DEPRECATED = "2021-01"
    MODERN = "2021-11"


class RechargeTokenAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Recharge-Access-Token": self._token}


class Orders(HttpStream, ABC):
    """
    Orders Stream: https://developer.rechargepayments.com/v1-shopify?python#list-orders
    Notes:
        Using `2021-01` the: `email`, `first_name`, `last_name` columns are not available,
        because these are not present in `2021-11` as DEPRECATED fields.
    """

    primary_key: str = "id"
    url_base: str = "https://api.rechargeapps.com/"
    cursor_field: str = "updated_at"
    page_size: int = 250
    page_num: int = 1
    period_in_days: int = 30  # Slice data request for 1 month
    raise_on_http_errors: bool = True
    state_checkpoint_interval: int = 250

    # registering the default schema transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Mapping[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self._start_date = config["start_date"]
        self.api_version = ApiVersion.DEPRECATED if config.get("use_orders_deprecated_api") else ApiVersion.MODERN

    @property
    def data_path(self) -> str:
        return self.name

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"x-recharge-version": self.api_version.value}

    def path(self, **kwargs) -> str:
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_token = None
        if self.api_version == ApiVersion.MODERN:
            cursor = response.json().get("next_cursor")
            if cursor:
                next_page_token = {"cursor": cursor}
        else:
            stream_data = self.get_stream_data(response.json())
            if len(stream_data) == self.page_size:
                self.page_num += 1
                next_page_token = {"page": self.page_num}
        return next_page_token

    def _update_params_with_min_max_date_range(
        self,
        params: MutableMapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params.update(
            {
                "sort_by": "updated_at-asc",
                "updated_at_min": (stream_slice or {}).get("start_date"),
                "updated_at_max": (stream_slice or {}).get("end_date"),
            }
        )
        return params

    def request_params(
        self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        if self.api_version == ApiVersion.MODERN:
            # if a cursor value is passed, only limit can be passed with it!
            if next_page_token:
                params.update(next_page_token)
            else:
                params = self._update_params_with_min_max_date_range(params, stream_slice)
            return params
        else:
            params = self._update_params_with_min_max_date_range(params, stream_slice)
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

    def get_error_handler(self) -> ErrorHandler:
        return RechargeErrorHandler(logger=self.logger)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date_value = (stream_state or {}).get(self.cursor_field, self._start_date) if self.cursor_field else self._start_date
        now = pendulum.now()
        # dates are inclusive, so we add 1 second so that time periods do not overlap
        start_date = pendulum.parse(start_date_value).add(seconds=1)
        while start_date <= now:
            end_date = start_date.add(days=self.period_in_days)
            yield {"start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"), "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S")}
            start_date = end_date.add(seconds=1)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}
