#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import math
from abc import ABC
from itertools import chain
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union, List

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class StripeStream(HttpStream, ABC):

    def __init__(self,  # *, url_base: str, start_date: int, account_id: str, headers: Mapping[str, str],
                 # request_parameters: Mapping[str, Any],
                 **kwargs):
        super().__init__()
        self.url_base = kwargs["url_base"]
        self.account_id = kwargs["account_id"]
        self.start_date = kwargs["start_date"]
        self._headers = kwargs["headers"]
        self._request_parameters = kwargs["request_parameters"]
        self._stream_to_cursor_field = kwargs["stream_to_cursor_field"]
        self._stream_to_path = kwargs["stream_to_path"]
        self._response_parser = kwargs["response_parser"]
        self._name = kwargs["name"]
        self._paginator = kwargs["paginator"]
        self._primary_key = kwargs["primary_key"]
        self._incremental_headers = kwargs["incremental_headers"]
        self._stream_to_parent_config = kwargs["stream_to_parent_config"]

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """Build complex PK based on slices and breakdowns"""
        return self._primary_key

    def path(
            self,
            *,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """
        _path = self._stream_to_path[self._name]
        _formatted = _path.format(stream_slice=stream_slice)
        return _path

    def url_base(self) -> str:
        return self._url_base

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        return self._paginator.next_page_token(decoded_response)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = self._request_parameters

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return self._headers

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        decoded_response = response.json()
        return self._response_parser.parse_response(decoded_response, **kwargs)


class IncrementalStripeAlexStream(StripeStream, ABC):
    # Stripe returns most recently created objects first, so we don't want to persist state until the entire stream has been read
    state_checkpoint_interval = math.inf

    def __init__(self, lookback_window_days: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window_days = lookback_window_days
        self._cursor_field = kwargs["stream_to_cursor_field"][self.name]

    @property
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        return self._cursor_field

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
        params.update(self._incremental_headers)
        params = {k: v.format(start_timestamp=start_timestamp) for k, v in params.items()}
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parent_name = self._stream_to_parent_config[self._name]["parent_name"]
        self._parent = meta_incremental(self.camel_to_snake(self._parent_name))
        self._parent_id = self._stream_to_parent_config[self._name]["parent_id"]
        self._sub_items_attr = self._stream_to_parent_config[self._name]["sub_items_attr"]
        self._parent_id_getter = self._stream_to_parent_config[self._name]["parent_id_getter"]

    def camel_to_snake(self, s: str) -> str:
        return ''.join(w.title() for w in s.split('_'))

    @property
    def parent(self) -> StripeStream:
        """
        :return: parent stream which contains needed records in <sub_items_attr>
        """
        return self._parent

    @property
    def parent_id(self) -> str:
        """
        :return: string with attribute name
        """
        return self._parent_id

    @property
    def sub_items_attr(self) -> str:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """
        return self._sub_items_attr

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        parent_stream = self.parent(
            **{
                "url_base": self.url_base,
                "account_id": self.account_id,
                "start_date": self.start_date,
                "headers": self._headers,
                "request_parameters": self._request_parameters,
                "stream_to_cursor_field": self._stream_to_cursor_field,
                "stream_to_path": self._stream_to_path,
                "response_parser": self._response_parser,
                "name": self._parent_name,
                "paginator": self._paginator,
                "primary_key": self._primary_key,
                "incremental_headers": self._incremental_headers,
                "stream_to_parent_config": self._stream_to_parent_config
            }
        )
        for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            # A lot of this belongs to the response_parser

            items_obj = record.get(self.sub_items_attr, {})
            if not items_obj:
                continue

            items = self._response_parser.parse_response(items_obj)

            # non-generic filter, mainly for BankAccounts stream only
            # FIXME: Need to implement this
            # if self.filter:
            #    items = [i for i in items if i.get(self.filter["attr"]) == self.filter["value"]]

            if not items:
                return

            # get next pages
            # this belongs to the paginator
            items_next_pages = []
            next_page_header = self._paginator.next_page_token(items_obj)
            if next_page_header is not None:
                parent_id = self._parent_id_getter.format(record=AttrDict(**item))
                stream_slice = {self.parent_id: parent_id, **next_page_header}
                items_next_pages = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, **kwargs)

            for item in chain(items, items_next_pages):
                if self.add_parent_id:
                    parent_id = self._parent_id_getter.format(record=AttrDict(**item))
                    # add reference to parent object when item doesn't have it already
                    item[self.parent_id] = parent_id
                yield item


def meta_incremental(name):
    class cls(IncrementalStripeAlexStream):
        pass

    cls.__name__ = name
    return cls


def meta_sub(name):
    class cls(StripeSubStream):
        pass

    cls.__name__ = name
    return cls


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

# class InvoiceLineItems(StripeSubStream):
#    """
#    API docs: https://stripe.com/docs/api/invoices/invoice_lines
#    """

# name = "invoice_line_items"

# parent = meta_incremental("Invoices")
# parent_name = "invoices"
# parent_id: str = "invoice_id"
# sub_items_attr = "lines"
# add_parent_id = True

#   def __init__(self, **kwargs):
#       super().__init__(**kwargs)
