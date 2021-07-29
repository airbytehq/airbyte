#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from datetime import datetime, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import backoff
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from chargebee.api_error import OperationFailedError
from chargebee.list_result import ListResult
from chargebee.model import Model
from chargebee.models import Addon, Customer, Invoice, Order, Plan, Subscription

# Backoff params below
# according to Chargebee's guidance on rate limit
# https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_rate_limits
MAX_TRIES = 10  # arbitrary max_tries
MAX_TIME = 90  # because Chargebee API enforce a per-minute limit


class ChargebeeStream(Stream):
    primary_key = "id"
    cursor_field = "updated_at"
    page_size = 100
    api: Model = None

    def __init__(self, start_date: str):
        # Convert `start_date` to timestamp(UTC).
        self._start_date = int(datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())

    @property
    def state_checkpoint_interval(self) -> int:
        return self.page_size

    def next_page_token(self, list_result: ListResult) -> Optional[Mapping[str, Any]]:
        # Reference for Chargebee's pagination strategy below:
        # https://apidocs.chargebee.com/docs/api/#pagination_and_filtering
        next_offset = list_result.next_offset
        if next_offset:
            return {"offset": next_offset}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "limit": self.page_size,
            "include_deleted": "true",
            "sort_by[asc]": self.cursor_field,
        }

        if next_page_token:
            params.update(next_page_token)

        start_point = self._start_date
        if stream_state:
            start_point = max(start_point, stream_state[self.cursor_field])

        params[f"{self.cursor_field}[after]"] = start_point

        return params

    def parse_response(self, list_result: ListResult, **kwargs) -> Iterable[Mapping]:
        for message in list_result:
            yield message._response[self.name]

    @backoff.on_exception(
        backoff.expo,  # Exponential back-off
        OperationFailedError,  # Only on Chargebee's OperationFailedError
        max_tries=MAX_TRIES,
        max_time=MAX_TIME,
    )
    def _send_request(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> ListResult:
        """
        Just a wrapper to allow @backoff decorator
        Reference: https://apidocs.chargebee.com/docs/api/#error_codes_list
        """
        kwargs = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return self.api.list(kwargs)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Override airbyte_cdk Stream's `read_records` method.
        """
        stream_state = stream_state or {}
        pagination_completed = False

        next_page_token = None
        while not pagination_completed:
            # Request the ListResult object from Chargebee with back-off implemented through self._send_request().
            list_result = self._send_request(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

            yield from self.parse_response(list_result, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(list_result)
            if not next_page_token:
                pagination_completed = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Override airbyte_cdk Stream's `get_updated_state` method to get the latest Chargebee stream state.
        """
        state_value = current_stream_state or {}

        latest_cursor_value = latest_record.get(self.cursor_field)

        if latest_cursor_value:
            state_value = {"updated_at": latest_cursor_value}

        return state_value


class SubscriptionStream(ChargebeeStream):
    name = "subscription"
    api = Subscription


class CustomerStream(ChargebeeStream):
    name = "customer"
    api = Customer


class InvoiceStream(ChargebeeStream):
    name = "invoice"
    api = Invoice


class OrderStream(ChargebeeStream):
    name = "order"
    api = Order


class PlanStream(ChargebeeStream):
    name = "plan"
    api = Plan


class AddonStream(ChargebeeStream):
    name = "addon"
    api = Addon
