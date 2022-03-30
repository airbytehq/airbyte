#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import math
from abc import ABC, abstractmethod
from itertools import chain
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class StripeStream(HttpStream, ABC):
    url_base = "https://api.stripe.com/v1/"
    primary_key = "id"

    def __init__(self, start_date: int, account_id: str, headers: Mapping[str, str], **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.start_date = start_date
        self._headers = headers

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if bool(decoded_response.get("has_more", "False")) and decoded_response.get("data", []):
            last_object_id = decoded_response["data"][-1]["id"]
            return {"starting_after": last_object_id}

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        # Stripe default pagination is 10, max is 100
        # params = self._request_parameters
        params = {"limit": 100}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return self._headers

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])  # Stripe puts records in a container array "data"


class IncrementalStripeAlexStream(StripeStream, ABC):
    # Stripe returns most recently created objects first, so we don't want to persist state until the entire stream has been read
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
        return {self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, 0))}

    def request_params(self, stream_state: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)

        start_timestamp = self.get_start_timestamp(stream_state)
        if start_timestamp:
            params["created[gte]"] = start_timestamp
        return params

    def get_start_timestamp(self, stream_state) -> int:
        start_point = self.start_date
        if stream_state and self.cursor_field in stream_state:
            start_point = max(start_point, stream_state[self.cursor_field])

        if start_point and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            start_point = int(pendulum.from_timestamp(start_point).subtract(days=abs(self.lookback_window_days)).timestamp())

        return start_point


class StripeSubStream(StripeStream, ABC):
    """
    Research shows that records related to SubStream can be extracted from Parent streams which already
    contain 1st page of needed items. Thus, it significantly decreases a number of requests needed to get
    all item in parent stream, since parent stream returns 100 items per request.
    Note, in major cases, pagination requests are not performed because sub items are fully reported in parent streams

    For example:
    Line items are part of each 'invoice' record, so use Invoices stream because
    it allows bulk extraction:
        0.1.28 and below - 1 request extracts line items for 1 invoice (+ pagination reqs)
        0.1.29 and above - 1 request extracts line items for 100 invoices (+ pagination reqs)

    if line items object has indication for next pages ('has_more' attr)
    then use current stream to extract next pages. In major cases pagination requests
    are not performed because line items are fully reported in 'invoice' record

    Example for InvoiceLineItems and parent Invoice streams, record from Invoice stream:
        {
          "created": 1641038947,    <--- 'Invoice' record
          "customer": "cus_HezytZRkaQJC8W",
          "id": "in_1KD6OVIEn5WyEQxn9xuASHsD",    <---- value for 'parent_id' attribute
          "object": "invoice",
          "total": 0,
          ...
          "lines": {    <---- sub_items_attr
            "data": [
              {
                "id": "il_1KD6OVIEn5WyEQxnm5bzJzuA",    <---- 'Invoice' line item record
                "object": "line_item",
                ...
              },
              {...}
            ],
            "has_more": false,    <---- next pages from 'InvoiceLineItemsPaginated' stream
            "object": "list",
            "total_count": 2,
            "url": "/v1/invoices/in_1KD6OVIEn5WyEQxn9xuASHsD/lines"
          }
        }
    """

    filter: Optional[Mapping[str, Any]] = None
    add_parent_id: bool = False

    @property
    @abstractmethod
    def parent(self) -> StripeStream:
        """
        :return: parent stream which contains needed records in <sub_items_attr>
        """

    @property
    @abstractmethod
    def parent_id(self) -> str:
        """
        :return: string with attribute name
        """

    @property
    @abstractmethod
    def sub_items_attr(self) -> str:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)

        # add 'starting_after' param
        if not params.get("starting_after") and stream_slice and stream_slice.get("starting_after"):
            params["starting_after"] = stream_slice["starting_after"]

        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:

        parent_stream = self.parent(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)
        for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh):

            items_obj = record.get(self.sub_items_attr, {})
            if not items_obj:
                continue

            items = items_obj.get("data", [])

            # non-generic filter, mainly for BankAccounts stream only
            if self.filter:
                items = [i for i in items if i.get(self.filter["attr"]) == self.filter["value"]]

            # get next pages
            items_next_pages = []
            if items_obj.get("has_more") and items:
                stream_slice = {self.parent_id: record["id"], "starting_after": items[-1]["id"]}
                items_next_pages = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, **kwargs)

            for item in chain(items, items_next_pages):
                if self.add_parent_id:
                    # add reference to parent object when item doesn't have it already
                    item[self.parent_id] = record["id"]
                yield item


class Invoices(IncrementalStripeAlexStream):
    """
    API docs: https://stripe.com/docs/api/invoices/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "invoices"


class InvoiceLineItems(StripeSubStream):
    """
    API docs: https://stripe.com/docs/api/invoices/invoice_lines
    """

    name = "invoice_line_items"

    parent = Invoices
    parent_id: str = "invoice_id"
    sub_items_attr = "lines"
    add_parent_id = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"invoices/{stream_slice[self.parent_id]}/lines"


class InvoiceItems(IncrementalStripeAlexStream):
    """
    API docs: https://stripe.com/docs/api/invoiceitems/list
    """

    cursor_field = "date"
    name = "invoice_items"

    def path(self, **kwargs):
        return "invoiceitems"
