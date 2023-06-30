#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import math
from abc import ABC, abstractmethod
from itertools import chain
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_stripe.availability_strategy import StripeSubStreamAvailabilityStrategy

STRIPE_ERROR_CODES: List = [
    # stream requires additional permissions
    "more_permissions_required",
    # account_id doesn't have the access to the stream
    "account_invalid",
]


class StripeStream(HttpStream, ABC):
    url_base = "https://api.stripe.com/v1/"
    primary_key = "id"
    DEFAULT_SLICE_RANGE = 365
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, start_date: int, account_id: str, slice_range: int = DEFAULT_SLICE_RANGE, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.start_date = start_date
        self.slice_range = slice_range or self.DEFAULT_SLICE_RANGE

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if "has_more" in decoded_response and decoded_response["has_more"] and decoded_response.get("data", []):
            last_object_id = decoded_response["data"][-1]["id"]
            return {"starting_after": last_object_id}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # Stripe default pagination is 10, max is 100
        params = {"limit": 100}
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        if self.account_id:
            return {"Stripe-Account": self.account_id}
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])  # Stripe puts records in a container array "data"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            parsed_error = e.response.json()
            error_code = parsed_error.get("error", {}).get("code")
            error_message = parsed_error.get("message")
            # if the API Key doesn't have required permissions to particular stream, this stream will be skipped
            if status_code == 403 and error_code in STRIPE_ERROR_CODES:
                self.logger.warn(f"Stream {self.name} is skipped, due to {error_code}. Full message: {error_message}")
                pass
            else:
                self.logger.error(f"Syncing stream {self.name} is failed, due to {error_code}. Full message: {error_message}")


class BasePaginationStripeStream(StripeStream, ABC):
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        for key in ("created[gte]", "created[lte]"):
            if key in stream_slice:
                params[key] = stream_slice[key]
        return params

    def chunk_dates(self, start_date_ts: int) -> Iterable[Tuple[int, int]]:
        now = pendulum.now().int_timestamp
        step = int(pendulum.duration(days=self.slice_range).total_seconds())
        after_ts = start_date_ts
        while after_ts < now:
            before_ts = min(now, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for start, end in self.chunk_dates(self.start_date):
            yield {"created[gte]": start, "created[lte]": end}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            return []

        try:
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            parsed_error = e.response.json()
            error_code = parsed_error.get("error", {}).get("code")
            error_message = parsed_error.get("message")
            # if the API Key doesn't have required permissions to particular stream, this stream will be skipped
            if status_code == 403 and error_code in STRIPE_ERROR_CODES:
                self.logger.warn(f"Stream {self.name} is skipped, due to {error_code}. Full message: {error_message}")
                pass
            else:
                self.logger.error(f"Syncing stream {self.name} is failed, due to {error_code}. Full message: {error_message}")


class Accounts(BasePaginationStripeStream):
    """
    Docs: https://stripe.com/docs/api/accounts/list
    Even the endpoint allow to filter based on created the data usually don't have this field.
    """

    def path(self, **kwargs):
        return "accounts"
