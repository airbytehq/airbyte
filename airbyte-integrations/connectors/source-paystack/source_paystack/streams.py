#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from datetime import datetime

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from source_paystack.constants import PAYSTACK_API_BASE_URL, PAYSTACK_CREATED_AT


class PaystackStream(HttpStream, ABC):
    url_base = PAYSTACK_API_BASE_URL
    primary_key = "id"

    def __init__(self, start_date: int, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        page, pageCount = decoded_response['meta']['page'], response.json()['meta']['pageCount']

        if page != pageCount:
            return { "page": page + 1 }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"perPage": 200}
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])  # Paystack puts records in a container array "data"


class IncrementalPaystackStream(PaystackStream, ABC):
    # Paystack (like Stripe) returns most recently created objects first, so we don't want to persist state until the entire stream has been read
    state_checkpoint_interval = math.inf

    def __init__(self, lookback_window_days: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window_days = lookback_window_days

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field),
                current_stream_state.get(self.cursor_field, None),
                key=lambda d: pendulum.parse(d).int_timestamp if d else 0
            )
        }

    def request_params(self, stream_state: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)

        start_timestamp = self.get_start_timestamp(stream_state)
        if start_timestamp:
            params["from"] = start_timestamp
        return params

    def get_start_timestamp(self, stream_state) -> str:
        start_point = self.start_date
        if stream_state and self.cursor_field in stream_state:
            start_point = max(
                start_point,
                stream_state[self.cursor_field],
                key=lambda d: pendulum.parse(d).int_timestamp
            )

        if start_point and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            start_point = pendulum.parse(start_point)\
                .subtract(days=abs(self.lookback_window_days))\
                .isoformat()\
                .replace("+00:00", "Z")

        return start_point


class Customers(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#customer-list
    """

    cursor_field = PAYSTACK_CREATED_AT

    def path(self, **kwargs) -> str:
        return "customer"