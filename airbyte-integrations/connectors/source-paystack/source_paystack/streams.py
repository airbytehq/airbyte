#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class PaystackStream(HttpStream, ABC):
    url_base = "https://api.paystack.co/"
    primary_key = "id"

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = pendulum.parse(start_date).int_timestamp

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        page = decoded_response["meta"]["page"]
        pageCount = decoded_response["meta"]["pageCount"]

        if page < pageCount:
            return {"page": page + 1}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"perPage": 200}
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("data", [])  # Paystack puts records in a container array "data"


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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_record_created = latest_record.get(self.cursor_field)
        return {
            self.cursor_field: max(
                latest_record_created,
                current_stream_state.get(self.cursor_field, None),
                key=lambda d: pendulum.parse(d).int_timestamp if d else 0,
            )
        }

    def request_params(self, stream_state: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["from"] = self._get_start_date(stream_state)
        return params

    def _get_start_date(self, stream_state) -> str:
        start_point = self.start_date
        if stream_state and self.cursor_field in stream_state:
            stream_record_created = stream_state[self.cursor_field]
            start_point = max(start_point, pendulum.parse(stream_record_created).int_timestamp)

        if start_point and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            start_point = pendulum.from_timestamp(start_point).subtract(days=abs(self.lookback_window_days)).int_timestamp

        return pendulum.from_timestamp(start_point).isoformat().replace("+00:00", "Z")


class Customers(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#customer-list
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "customer"


class Disputes(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#dispute-list
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "dispute"


class Invoices(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#invoice-list
    """

    cursor_field = "created_at"

    def path(self, **kwargs) -> str:
        return "paymentrequest"


class Refunds(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#refund-list
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "refund"


class Settlements(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#settlement
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "settlement"


class Subscriptions(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#subscription-list
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "subscription"


class Transactions(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#transaction-list
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "transaction"


class Transfers(IncrementalPaystackStream):
    """
    API docs: https://paystack.com/docs/api/#transfer-list
    """

    cursor_field = "createdAt"

    def path(self, **kwargs) -> str:
        return "transfer"
