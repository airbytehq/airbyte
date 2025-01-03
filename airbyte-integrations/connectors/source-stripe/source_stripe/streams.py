#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import math
import os
from abc import ABC, abstractmethod
from itertools import chain
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ExponentialBackoffStrategy
from airbyte_cdk.sources.streams.checkpoint import Cursor
from airbyte_cdk.sources.streams.checkpoint.resumable_full_refresh_cursor import ResumableFullRefreshCursor
from airbyte_cdk.sources.streams.checkpoint.substream_resumable_full_refresh_cursor import SubstreamResumableFullRefreshCursor
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_stripe.error_handlers import ParentIncrementalStripeSubStreamErrorHandler, StripeErrorHandler
from source_stripe.error_mappings import PARENT_INCREMENTAL_STRIPE_SUB_STREAM_ERROR_MAPPING


STRIPE_API_VERSION = "2022-11-15"
CACHE_DISABLED = os.environ.get("CACHE_DISABLED")
IS_TESTING = os.environ.get("DEPLOYMENT_MODE") == "testing"
USE_CACHE = not CACHE_DISABLED


class IRecordExtractor(ABC):
    @abstractmethod
    def extract_records(self, records: Iterable[MutableMapping], stream_slice: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        pass


class DefaultRecordExtractor(IRecordExtractor):
    def __init__(self, response_filter: Optional[Callable] = None, slice_data_retriever: Optional[Callable] = None):
        self._response_filter = response_filter or (lambda record: record)
        self._slice_data_retriever = slice_data_retriever or (lambda record, *_: record)

    def extract_records(
        self, records: Iterable[MutableMapping], stream_slice: Optional[Mapping[str, Any]] = None
    ) -> Iterable[MutableMapping]:
        yield from filter(self._response_filter, map(lambda x: self._slice_data_retriever(x, stream_slice), records))


class EventRecordExtractor(DefaultRecordExtractor):
    def __init__(self, cursor_field: str, response_filter: Optional[Callable] = None, slice_data_retriever: Optional[Callable] = None):
        super().__init__(response_filter, slice_data_retriever)
        self.cursor_field = cursor_field

    def extract_records(
        self, records: Iterable[MutableMapping], stream_slice: Optional[Mapping[str, Any]] = None
    ) -> Iterable[MutableMapping]:
        for record in records:
            item = record["data"]["object"]
            item[self.cursor_field] = record["created"]
            if record["type"].endswith(".deleted"):
                item["is_deleted"] = True
            if self._response_filter(item):
                yield self._slice_data_retriever(item, stream_slice)


class UpdatedCursorIncrementalRecordExtractor(DefaultRecordExtractor):
    def __init__(
        self,
        cursor_field: str,
        legacy_cursor_field: Optional[str],
        response_filter: Optional[Callable] = None,
        slice_data_retriever: Optional[Callable] = None,
    ):
        super().__init__(response_filter, slice_data_retriever)
        self.cursor_field = cursor_field
        self.legacy_cursor_field = legacy_cursor_field

    def extract_records(
        self, records: Iterable[MutableMapping], stream_slice: Optional[Mapping[str, Any]] = None
    ) -> Iterable[MutableMapping]:
        records = super().extract_records(records, stream_slice)
        for record in records:
            if self.cursor_field in record:
                yield record
                continue  # Skip the rest of the loop iteration
            # fetch legacy_cursor_field from record; default to current timestamp for initial syncs without an any cursor.
            current_cursor_value = record.get(self.legacy_cursor_field, pendulum.now().int_timestamp)

            # yield the record with the added cursor_field
            yield record | {self.cursor_field: current_cursor_value}


class StripeStream(HttpStream, ABC):
    is_resumable = False
    url_base = "https://api.stripe.com/v1/"
    DEFAULT_SLICE_RANGE = 365
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return StripeErrorHandler(logger=self.logger)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return super().name

    def path(self, *args, **kwargs) -> str:
        if self._path:
            return self._path if isinstance(self._path, str) else self._path(self, *args, **kwargs)
        return super().path(*args, **kwargs)

    @property
    def use_cache(self) -> bool:
        return self._use_cache

    @property
    def expand_items(self) -> Optional[List[str]]:
        return self._expand_items

    def extra_request_params(self, *args, **kwargs) -> Mapping[str, Any]:
        if callable(self._extra_request_params):
            return self._extra_request_params(self, *args, **kwargs)
        return self._extra_request_params or {}

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return ExponentialBackoffStrategy(config={}, parameters={}, factor=1)

    @property
    def record_extractor(self) -> IRecordExtractor:
        return self._record_extractor

    def __init__(
        self,
        start_date: int,
        account_id: str,
        *args,
        slice_range: int = DEFAULT_SLICE_RANGE,
        record_extractor: Optional[IRecordExtractor] = None,
        name: Optional[str] = None,
        path: Optional[Union[Callable, str]] = None,
        use_cache: bool = False,
        expand_items: Optional[List[str]] = None,
        extra_request_params: Optional[Union[Mapping[str, Any], Callable]] = None,
        response_filter: Optional[Callable] = None,
        slice_data_retriever: Optional[Callable] = None,
        primary_key: Optional[str] = "id",
        **kwargs,
    ):
        self.account_id = account_id
        self.start_date = start_date
        self.slice_range = slice_range or self.DEFAULT_SLICE_RANGE
        self._record_extractor = record_extractor or DefaultRecordExtractor(response_filter, slice_data_retriever)
        self._name = name
        self._path = path
        self._use_cache = use_cache
        self._expand_items = expand_items
        self._extra_request_params = extra_request_params
        self._primary_key = primary_key
        super().__init__(*args, **kwargs)

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
        params = {
            "limit": 100,
            **self.extra_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        }
        if self.expand_items:
            params["expand[]"] = self.expand_items
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from self.record_extractor.extract_records(response.json().get("data", []), stream_slice)

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        headers = {"Stripe-Version": STRIPE_API_VERSION}
        if self.account_id:
            headers["Stripe-Account"] = self.account_id
        return headers

    def retry_factor(self) -> float:
        """
        Override for testing purposes
        """
        return 0 if IS_TESTING else super(StripeStream, self).retry_factor

    def get_cursor(self) -> Optional[Cursor]:
        """
        RFR is breaking the pagination in Stripe today. The stream is instantiated using the stream facade here. During the read, this goes
        through the concurrent code here so that we can read full refresh streams concurrently.

        However, as there are no cursors and the read records is the one from the HttpStream, we end up assigning the
        ResumableFullRefresCursor and hence only read a single page.

        In order to avoid that, we will assume there are no cursor if the cursor if RFR.
        """
        parent_cursor = super().get_cursor()
        if isinstance(parent_cursor, (ResumableFullRefreshCursor, SubstreamResumableFullRefreshCursor)):
            return None
        return parent_cursor


class IStreamSelector(ABC):
    @abstractmethod
    def get_parent_stream(self, stream_state: Mapping[str, Any]) -> StripeStream:
        pass


class CreatedCursorIncrementalStripeStream(StripeStream):
    is_resumable = True
    # Stripe returns most recently created objects first, so we don't want to persist state until the entire stream has been read
    state_checkpoint_interval = math.inf

    @property
    def cursor_field(self) -> str:
        return self._cursor_field

    def __init__(
        self,
        *args,
        lookback_window_days: int = 0,
        start_date_max_days_from_now: Optional[int] = None,
        cursor_field: str = "created",
        **kwargs,
    ):
        self._cursor_field = cursor_field
        super().__init__(*args, **kwargs)
        self.lookback_window_days = lookback_window_days
        self.start_date_max_days_from_now = start_date_max_days_from_now

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        state_cursor_value = current_stream_state.get(self.cursor_field, 0)
        latest_record_value = latest_record.get(self.cursor_field)
        if state_cursor_value:
            return {self.cursor_field: max(latest_record_value, state_cursor_value)}
        return {self.cursor_field: latest_record_value}

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super(CreatedCursorIncrementalStripeStream, self).request_params(stream_state, stream_slice, next_page_token)
        return {"created[gte]": stream_slice["created[gte]"], "created[lte]": stream_slice["created[lte]"], **params}

    def chunk_dates(self, start_date_ts: int) -> Iterable[Tuple[int, int]]:
        now = pendulum.now().int_timestamp
        step = int(pendulum.duration(days=self.slice_range).total_seconds())
        after_ts = start_date_ts
        while after_ts < now:
            before_ts = min(now, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}
        start_ts = self.get_start_timestamp(stream_state)
        if start_ts >= pendulum.now().int_timestamp:
            return []
        for start, end in self.chunk_dates(start_ts):
            yield {"created[gte]": start, "created[lte]": end}

    def get_start_timestamp(self, stream_state) -> int:
        start_point = self.start_date
        # we use +1 second because date range is inclusive
        start_point = max(start_point, stream_state.get(self.cursor_field, 0) + 1)

        if start_point and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            start_point = int(pendulum.from_timestamp(start_point).subtract(days=abs(self.lookback_window_days)).timestamp())

        if self.start_date_max_days_from_now:
            allowed_start_date = pendulum.now().subtract(days=self.start_date_max_days_from_now).int_timestamp
            if start_point < allowed_start_date:
                self.logger.info(
                    f"Applying the restriction of maximum {self.start_date_max_days_from_now} days lookback to stream {self.name}"
                )
                start_point = allowed_start_date
        return start_point


class Events(CreatedCursorIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/events/list
    """

    def __init__(self, *args, event_types: Optional[Iterable[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_types = event_types

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.event_types:
            if len(self.event_types) > 1:
                params["types[]"] = self.event_types
            else:
                params["type"] = self.event_types
        return params

    def path(self, **kwargs):
        return "events"


class UpdatedCursorIncrementalStripeStream(StripeStream):
    is_resumable = True
    """
    `CreatedCursorIncrementalStripeStream` does not provide a way to read updated data since given date because the API does not allow to do this.
    It only returns newly created entities since given date. So to have all the updated data as well we need to make use of the Events API,
    which allows to retrieve updated data since given date for a number of predefined events which are associated with the corresponding
    entities.
    """

    @property
    def cursor_field(self):
        return self._cursor_field

    @property
    def legacy_cursor_field(self):
        return self._legacy_cursor_field

    @property
    def event_types(self) -> Iterable[str]:
        """A list of event types that are associated with entity."""
        return self._event_types

    def __init__(
        self,
        *args,
        cursor_field: str = "updated",
        legacy_cursor_field: Optional[str] = "created",
        event_types: Optional[List[str]] = None,
        record_extractor: Optional[IRecordExtractor] = None,
        response_filter: Optional[Callable] = None,
        **kwargs,
    ):
        self._event_types = event_types
        self._cursor_field = cursor_field
        self._legacy_cursor_field = legacy_cursor_field
        record_extractor = record_extractor or UpdatedCursorIncrementalRecordExtractor(
            self.cursor_field, self.legacy_cursor_field, response_filter
        )
        super().__init__(*args, record_extractor=record_extractor, **kwargs)
        # `lookback_window_days` is hardcoded as it does not make any sense to re-export events,
        # as each event holds the latest value of a record.
        # `start_date_max_days_from_now` represents the events API limitation.
        self.events_stream = Events(
            authenticator=kwargs.get("authenticator"),
            lookback_window_days=0,
            start_date_max_days_from_now=30,
            account_id=self.account_id,
            start_date=self.start_date,
            slice_range=self.slice_range,
            event_types=self.event_types,
            cursor_field=self.cursor_field,
            record_extractor=EventRecordExtractor(cursor_field=self.cursor_field, response_filter=response_filter),
        )

    def update_cursor_field(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if not self.legacy_cursor_field:
            # Streams that used to support only full_refresh mode.
            # Now they support event-based incremental syncs but have a cursor field only in that mode.
            return stream_state
        # support for both legacy and new cursor fields
        current_stream_state_value = stream_state.get(self.cursor_field, stream_state.get(self.legacy_cursor_field, 0))
        return {self.cursor_field: current_stream_state_value}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_record_value = latest_record.get(self.cursor_field)
        current_stream_state = self.update_cursor_field(current_stream_state)
        current_state_value = current_stream_state.get(self.cursor_field)
        if current_state_value:
            return {self.cursor_field: max(latest_record_value, current_state_value)}
        return {self.cursor_field: latest_record_value}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # When reading from a stream, a `read_records` is called once per slice.
        # We yield a single slice here because we don't want to make duplicate calls for event based incremental syncs.
        yield {}

    def read_event_increments(
        self, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[StreamData]:
        stream_state = self.update_cursor_field(stream_state or {})
        for event_slice in self.events_stream.stream_slices(
            sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_state=stream_state
        ):
            yield from self.events_stream.read_records(
                SyncMode.incremental, cursor_field=cursor_field, stream_slice=event_slice, stream_state=stream_state
            )

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        if not stream_state:
            # both full refresh and initial incremental sync should use usual endpoints
            yield from super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)
            return
        yield from self.read_event_increments(cursor_field=cursor_field, stream_state=stream_state)


class IncrementalStripeStreamSelector(IStreamSelector):
    def __init__(
        self,
        created_cursor_incremental_stream: CreatedCursorIncrementalStripeStream,
        updated_cursor_incremental_stream: UpdatedCursorIncrementalStripeStream,
    ):
        self._created_cursor_stream = created_cursor_incremental_stream
        self._updated_cursor_stream = updated_cursor_incremental_stream

    def get_parent_stream(self, stream_state: Mapping[str, Any]) -> StripeStream:
        return self._updated_cursor_stream if stream_state else self._created_cursor_stream


class IncrementalStripeStream(StripeStream):
    is_resumable = True
    """
    This class combines both normal incremental sync and event based sync. It uses common endpoints for sliced data syncs in
    the full refresh sync mode and initial incremental sync. For incremental syncs with a state, event based sync comes into action.
    """

    def __init__(
        self,
        *args,
        cursor_field: str = "updated",
        legacy_cursor_field: Optional[str] = "created",
        event_types: Optional[List[str]] = None,
        **kwargs,
    ):
        self._cursor_field = cursor_field
        super().__init__(*args, **kwargs)
        created_cursor_stream = CreatedCursorIncrementalStripeStream(
            *args,
            cursor_field=cursor_field,
            # `lookback_window_days` set to 0 because this particular instance is in charge of full_refresh/initial incremental syncs only
            lookback_window_days=0,
            record_extractor=UpdatedCursorIncrementalRecordExtractor(cursor_field, legacy_cursor_field),
            **kwargs,
        )
        updated_cursor_stream = UpdatedCursorIncrementalStripeStream(
            *args,
            cursor_field=cursor_field,
            legacy_cursor_field=legacy_cursor_field,
            event_types=event_types,
            **kwargs,
        )
        self._parent_stream = None
        self.stream_selector = IncrementalStripeStreamSelector(created_cursor_stream, updated_cursor_stream)

    @property
    def parent_stream(self):
        return self._parent_stream

    @parent_stream.setter
    def parent_stream(self, stream):
        self._parent_stream = stream

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._cursor_field

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.parent_stream = self.stream_selector.get_parent_stream(stream_state)
        yield from self.parent_stream.stream_slices(sync_mode, cursor_field, stream_state)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.parent_stream.get_updated_state(current_stream_state, latest_record)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self.parent_stream.read_records(sync_mode, cursor_field, stream_slice, stream_state)


class SetupAttempts(CreatedCursorIncrementalStripeStream, HttpSubStream):
    """
    Docs: https://stripe.com/docs/api/setup_attempts/list
    """

    def __init__(self, **kwargs):
        # SetupAttempts needs lookback_window, but it's parent class does not
        parent_kwargs = copy.copy(kwargs)
        parent_kwargs.pop("lookback_window_days")
        parent = IncrementalStripeStream(
            name="setup_intents",
            path="setup_intents",
            event_types=[
                "setup_intent.canceled",
                "setup_intent.created",
                "setup_intent.requires_action",
                "setup_intent.setup_failed",
                "setup_intent.succeeded",
            ],
            **parent_kwargs,
        )
        super().__init__(parent=parent, **kwargs)

    def path(self, **kwargs) -> str:
        return "setup_attempts"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # this is a unique combination of CreatedCursorIncrementalStripeStream and HttpSubStream,
        # so we need to have all the parent IDs multiplied by all the date slices
        incremental_slices = list(
            CreatedCursorIncrementalStripeStream.stream_slices(
                self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state
            )
        )
        if incremental_slices:
            parent_records = HttpSubStream.stream_slices(self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
            yield from (slice | rec for rec in parent_records for slice in incremental_slices)
        else:
            yield from []

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        setup_intent_id = stream_slice.get("parent", {}).get("id")
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update(setup_intent=setup_intent_id)
        return params


class StripeSubStream(StripeStream, HttpSubStream):
    pass


class StripeLazySubStream(StripeStream, HttpSubStream):
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

    @property
    def sub_items_attr(self) -> str:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """
        return self._sub_items_attr

    def __init__(
        self,
        *args,
        sub_items_attr: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._sub_items_attr = sub_items_attr

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)

        # add 'starting_after' param
        if not params.get("starting_after") and stream_slice and stream_slice.get("starting_after"):
            params["starting_after"] = stream_slice["starting_after"]

        return params

    def read_records(self, sync_mode: SyncMode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        items_obj = stream_slice["parent"].get(self.sub_items_attr, {})
        if not items_obj:
            return

        items_next_pages = []
        items = list(self.record_extractor.extract_records(items_obj.get("data", []), stream_slice))
        if items_obj.get("has_more") and items:
            stream_slice = {"starting_after": items[-1]["id"], **stream_slice}
            items_next_pages = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, **kwargs)
        yield from chain(items, items_next_pages)


class IncrementalStripeLazySubStreamSelector(IStreamSelector):
    def __init__(self, updated_cursor_incremental_stream: UpdatedCursorIncrementalStripeStream, lazy_sub_stream: StripeLazySubStream):
        self._updated_incremental_stream = updated_cursor_incremental_stream
        self._lazy_sub_stream = lazy_sub_stream

    def get_parent_stream(self, stream_state: Mapping[str, Any]) -> StripeStream:
        return self._updated_incremental_stream if stream_state else self._lazy_sub_stream


class UpdatedCursorIncrementalStripeLazySubStream(StripeStream, ABC):
    is_resumable = True
    """
    This stream uses StripeLazySubStream under the hood to run full refresh or initial incremental syncs.
    In case of subsequent incremental syncs, it uses the UpdatedCursorIncrementalStripeStream class.
    """

    def __init__(
        self,
        parent: StripeStream,
        *args,
        cursor_field: str = "updated",
        legacy_cursor_field: Optional[str] = "created",
        event_types: Optional[List[str]] = None,
        sub_items_attr: Optional[str] = None,
        response_filter: Optional[Callable] = None,
        **kwargs,
    ):
        self._cursor_field = cursor_field
        super().__init__(*args, **kwargs)
        self.updated_cursor_incremental_stream = UpdatedCursorIncrementalStripeStream(
            *args,
            cursor_field=cursor_field,
            legacy_cursor_field=legacy_cursor_field,
            event_types=event_types,
            response_filter=response_filter,
            **kwargs,
        )
        self.lazy_substream = StripeLazySubStream(
            *args,
            parent=parent,
            sub_items_attr=sub_items_attr,
            record_extractor=UpdatedCursorIncrementalRecordExtractor(
                cursor_field=cursor_field,
                legacy_cursor_field=legacy_cursor_field,
                response_filter=response_filter,
                slice_data_retriever=kwargs.get("slice_data_retriever"),
            ),
            **kwargs,
        )
        self._parent_stream = None
        self.stream_selector = IncrementalStripeLazySubStreamSelector(self.updated_cursor_incremental_stream, self.lazy_substream)

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._cursor_field

    @property
    def parent_stream(self):
        return self._parent_stream

    @parent_stream.setter
    def parent_stream(self, stream):
        self._parent_stream = stream

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.parent_stream = self.stream_selector.get_parent_stream(stream_state)
        yield from self.parent_stream.stream_slices(sync_mode, cursor_field=cursor_field, stream_state=stream_state)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # important note: do not call self.parent_stream here as one of the parents does not have the needed method implemented
        return self.updated_cursor_incremental_stream.get_updated_state(current_stream_state, latest_record)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self.parent_stream.read_records(
            sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        )


class ParentIncrementalStripeSubStream(StripeSubStream):
    is_resumable = True
    """
    This stream differs from others in that it runs parent stream in exactly same sync mode it is run itself to generate stream slices.
    It also uses regular /v1 API endpoints to sync data no matter what the sync mode is. This means that the event-based API can only
    be utilized by the parent stream.
    """

    @property
    def cursor_field(self) -> str:
        return self._cursor_field

    def __init__(self, cursor_field: str, *args, **kwargs):
        self._cursor_field = cursor_field
        super().__init__(*args, **kwargs)

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}
        if stream_state:
            # state is shared between self and parent, but cursor fields are different
            stream_state = {self.parent.cursor_field: stream_state.get(self.cursor_field, 0)}
        parent_stream_slices = self.parent.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"parent": record}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(current_stream_state.get(self.cursor_field, 0), latest_record[self.cursor_field])}

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return ParentIncrementalStripeSubStreamErrorHandler(
            logger=self.logger, error_mapping=PARENT_INCREMENTAL_STRIPE_SUB_STREAM_ERROR_MAPPING
        )


class UpdatedCursorIncrementalStripeSubStream(UpdatedCursorIncrementalStripeStream, HttpSubStream):
    """
    This class behaves exactly the same as its parent, UpdatedCursorIncrementalStripeStream, but the initial/full refresh sync is performed using the parent stream.
    """

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if not stream_state:
            yield from HttpSubStream.stream_slices(self, sync_mode, cursor_field, stream_state)
        else:
            yield from UpdatedCursorIncrementalStripeStream.stream_slices(self, sync_mode, cursor_field, stream_state)
