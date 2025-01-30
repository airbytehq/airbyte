#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum as pdm
import requests
from requests.exceptions import RequestException
from source_shopify.http_request import ShopifyErrorHandler
from source_shopify.shopify_graphql.bulk.job import ShopifyBulkManager
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkQuery
from source_shopify.transform import DataTypeEnforcer
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache
from source_shopify.utils import ShopifyNonRetryableErrors
from source_shopify.utils import ShopifyRateLimiter as limiter

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpClient, HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING


class ShopifyStream(HttpStream, ABC):
    # define default logger
    logger = logging.getLogger("airbyte")

    # Latest Stable Release
    api_version = "2024-04"
    # Page size
    limit = 250

    primary_key = "id"
    order_field = "updated_at"
    filter_field = "updated_at_min"

    def __init__(self, config: Dict) -> None:
        super().__init__(authenticator=config["authenticator"])
        self._transformer = DataTypeEnforcer(self.get_json_schema())
        self.config = config

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""

    @property
    def url_base(self) -> str:
        return f"https://{self.config['shop']}.myshopify.com/admin/api/{self.api_version}/"

    @property
    def default_filter_field_value(self) -> Union[int, str]:
        # certain streams are using `since_id` field as `filter_field`, which requires to use `int` type,
        # but many other use `str` values for this, we determine what to use based on `filter_field` value
        # by default, we use the user defined `Start Date` as initial value, or 0 for `id`-dependent streams.
        return 0 if self.filter_field == "since_id" else (self.config.get("start_date") or "")

    def path(self, **kwargs) -> str:
        return f"{self.data_field}.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(self, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        else:
            params["order"] = f"{self.order_field} asc"
            params[self.filter_field] = self.default_filter_field_value
        return params

    @limiter.balance_rate_limit()
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code is requests.codes.OK:
            try:
                json_response = response.json()
                records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
                yield from self.produce_records(records)
            except RequestException as e:
                self.logger.warning(f"Unexpected error in `parse_ersponse`: {e}, the actual response data: {response.text}")
                yield {}

    def produce_records(
        self, records: Optional[Union[Iterable[Mapping[str, Any]], Mapping[str, Any]]] = None
    ) -> Iterable[Mapping[str, Any]]:
        # transform method was implemented according to issue 4841
        # Shopify API returns price fields as a string and it should be converted to number
        # this solution designed to convert string into number, but in future can be modified for general purpose
        if isinstance(records, dict):
            # for cases when we have a single record as dict
            # add shop_url to the record to make querying easy
            records["shop_url"] = self.config["shop"]
            yield self._transformer.transform(records)
        else:
            # for other cases
            for record in records:
                # add shop_url to the record to make querying easy
                record["shop_url"] = self.config["shop"]
                yield self._transformer.transform(record)

    def get_error_handler(self) -> Optional[ErrorHandler]:
        known_errors = ShopifyNonRetryableErrors(self.name)
        error_mapping = DEFAULT_ERROR_MAPPING | known_errors
        return HttpStatusErrorHandler(self.logger, max_retries=5, error_mapping=error_mapping)


class ShopifyDeletedEventsStream(ShopifyStream):
    data_field = "events"
    primary_key = "id"
    cursor_field = "deleted_at"

    def __init__(self, config: Dict, deleted_events_api_name: str) -> None:
        self.deleted_events_api_name = deleted_events_api_name
        super().__init__(config)

    @property
    def availability_strategy(self) -> None:
        """
        No need to apply the `availability strategy` for this service stream.
        """
        return None

    def get_json_schema(self) -> None:
        """
        No need to apply the `schema` for this service stream.
        Return `{}` to satisfy the `self._transformer.transform(record)` logic.
        """
        return {}

    def produce_deleted_records_from_events(self, delete_events: Iterable[Mapping[str, Any]] = []) -> Iterable[Mapping[str, Any]]:
        for event in delete_events:
            yield {
                "id": event["subject_id"],
                self.cursor_field: event["created_at"],
                "deleted_message": event.get("message", None),
                "deleted_description": event.get("description", None),
                "shop_url": event["shop_url"],
            }

    def read_records(self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        delete_events = super().read_records(stream_state=stream_state, **kwargs)
        yield from self.produce_deleted_records_from_events(delete_events)

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> MutableMapping[str, Any]:
        params: Mapping[str, Any] = {}

        if next_page_token:
            # `filter` and `verb` cannot be passed, when `page_info` is present.
            # See https://shopify.dev/api/usage/pagination-rest
            params.update(**next_page_token)
        else:
            params.update(**{"filter": self.deleted_events_api_name, "verb": "destroy"})
            if stream_state:
                state = stream_state.get("deleted", {}).get(self.cursor_field)
                if state:
                    params["created_at_min"] = state
        return params


class IncrementalShopifyStream(ShopifyStream, ABC):
    # Setting the check point interval to the limit of the records output
    state_checkpoint_interval = 250

    @property
    def filter_by_state_checkpoint(self) -> bool:
        """
        This filtering flag stands to guarantee for the NestedSubstreams to emit the STATE correctly,
        when we have the abnormal STATE distance between Parent and Substream
        """
        return False

    # Setting the default cursor field for all streams
    cursor_field = "updated_at"
    deleted_cursor_field = "deleted_at"
    _checkpoint_cursor = None

    @property
    def default_state_comparison_value(self) -> Union[int, str]:
        # certain streams are using `id` field as `cursor_field`, which requires to use `int` type,
        # but many other use `str` values for this, we determine what to use based on `cursor_field` value
        return 0 if self.cursor_field == "id" else ""

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        last_record_value = latest_record.get(self.cursor_field) or self.default_state_comparison_value
        current_state_value = current_stream_state.get(self.cursor_field) or self.default_state_comparison_value
        return {self.cursor_field: max(last_record_value, current_state_value)}

    @stream_state_cache.cache_stream_state
    def request_params(
        self, stream_state: Optional[Mapping[str, Any]] = None, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["order"] = f"{self.order_field} asc"
            if stream_state:
                params[self.filter_field] = stream_state.get(self.cursor_field)
        return params

    def track_checkpoint_cursor(self, record_value: Union[str, int]) -> None:
        if self.filter_by_state_checkpoint:
            # set checkpoint cursor
            if not self._checkpoint_cursor:
                self._checkpoint_cursor = self.default_state_comparison_value
            # track checkpoint cursor
            if str(record_value) >= str(self._checkpoint_cursor):
                self._checkpoint_cursor = record_value

    def should_checkpoint(self, index: int) -> bool:
        return self.filter_by_state_checkpoint and index >= self.state_checkpoint_interval

    # Parse the `records` with respect to the `stream_state` for the `Incremental refresh`
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        records_slice: Optional[Iterable[Mapping]] = None,
    ) -> Iterable:
        # Getting records >= state
        if stream_state:
            state_value = stream_state.get(self.cursor_field, self.default_state_comparison_value)
            for index, record in enumerate(records_slice, 1):
                if self.cursor_field in record:
                    record_value = record.get(self.cursor_field, self.default_state_comparison_value)
                    self.track_checkpoint_cursor(record_value)
                    if record_value:
                        if record_value >= state_value:
                            yield record
                        else:
                            if self.should_checkpoint(index):
                                yield record
                    else:
                        # old entities could have cursor field in place, but set to null
                        self.logger.warning(
                            f"Stream `{self.name}`, Record ID: `{record.get(self.primary_key)}` cursor value is: {record_value}, record is emitted without state comparison"
                        )
                        yield record
                else:
                    # old entities could miss the cursor field
                    self.logger.warning(
                        f"Stream `{self.name}`, Record ID: `{record.get(self.primary_key)}` missing cursor field: {self.cursor_field}, record is emitted without state comparison"
                    )
                    yield record
        else:
            yield from records_slice


class IncrementalShopifySubstream(IncrementalShopifyStream):
    """
    IncrementalShopifySubstream - provides slicing functionality for streams using parts of data from parent stream.
    For example:
       - `Refunds Orders` is the entity of `Orders`,
       - `OrdersRisks` is the entity of `Orders`,
       - `DiscountCodes` is the entity of `PriceRules`, etc.

    ::  @ parent_stream - defines the parent stream object to read from
    ::  @ slice_key - defines the name of the property in stream slices dict.
    ::  @ nested_record - the name of the field inside of parent stream record. Default is `id`.
    ::  @ nested_record_field_name - the name of the field inside of nested_record.
    ::  @ nested_substream - the name of the nested entity inside of parent stream, helps to reduce the number of
          API Calls, if present, see `OrderRefunds` stream for more.
    """

    parent_stream_class: Union[ShopifyStream, IncrementalShopifyStream] = None
    slice_key: str = None
    nested_record: str = "id"
    nested_record_field_name: str = None
    nested_substream = None
    nested_substream_list_field_id = None

    @cached_property
    def parent_stream(self) -> Union[ShopifyStream, IncrementalShopifyStream]:
        """
        Returns the instance of parent stream, if the substream has a `parent_stream_class` dependency.
        """
        return self.parent_stream_class(self.config) if self.parent_stream_class else None

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        """UPDATING THE STATE OBJECT:
        Stream: Transactions
        Parent Stream: Orders
        Returns:
            {
                {...},
                "transactions": {
                    "created_at": "2022-03-03T03:47:45-08:00",
                    "orders": {
                        "updated_at": "2022-03-03T03:47:46-08:00"
                    }
                },
                {...},
            }
        """
        updated_state = super().get_updated_state(current_stream_state, latest_record)
        # add parent_stream_state to `updated_state`
        updated_state[self.parent_stream.name] = stream_state_cache.cached_state.get(self.parent_stream.name)
        return updated_state

    def request_params(self, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def stream_slices(self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Reading the parent stream for slices with structure:
        EXAMPLE: for given nested_record as `id` of Orders,

        Outputs:
            [
                {slice_key: 123},
                {slice_key: 456},
                {...},
                {slice_key: 999
            ]
        """
        sorted_substream_slices = []

        # reading parent nested stream_state from child stream state
        parent_stream_state = stream_state.get(self.parent_stream.name) if stream_state else {}

        # reading the parent stream
        for record in self.parent_stream.read_records(stream_state=parent_stream_state, **kwargs):
            # updating the `stream_state` with the state of it's parent stream
            # to have the child stream sync independently from the parent stream
            stream_state_cache.cached_state[self.parent_stream.name] = self.parent_stream.get_updated_state({}, record)
            # to limit the number of API Calls and reduce the time of data fetch,
            # we can pull the ready data for child_substream, if nested data is present,
            # and corresponds to the data of child_substream we need.
            if self.nested_substream and self.nested_substream_list_field_id:
                if record.get(self.nested_substream):
                    sorted_substream_slices.extend(
                        [
                            {
                                self.slice_key: sub_record[self.nested_substream_list_field_id],
                                self.cursor_field: record[self.nested_substream][0].get(
                                    self.cursor_field, self.default_state_comparison_value
                                ),
                            }
                            for sub_record in record[self.nested_record]
                        ]
                    )
            elif self.nested_substream:
                if record.get(self.nested_substream):
                    sorted_substream_slices.append(
                        {
                            self.slice_key: record[self.nested_record],
                            self.cursor_field: record[self.nested_substream][0].get(self.cursor_field, self.default_state_comparison_value),
                        }
                    )
            else:
                # avoid checking `deleted` records for substreams, a.k.a `Metafields` streams,
                # since `deleted` records are not available, thus we avoid HTTP-400 errors.
                if self.deleted_cursor_field not in record:
                    yield {self.slice_key: record[self.nested_record]}

        # output slice from sorted list to avoid filtering older records
        if self.nested_substream:
            if len(sorted_substream_slices) > 0:
                # sort by cursor_field
                sorted_substream_slices.sort(key=lambda x: x.get(self.cursor_field))
                for sorted_slice in sorted_substream_slices:
                    yield {self.slice_key: sorted_slice[self.slice_key]}

    # the stream_state caching is required to avoid the STATE collisions for Substreams
    @stream_state_cache.cache_stream_state
    def read_records(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """Reading child streams records for each `id`"""

        slice_data = stream_slice.get(self.slice_key)
        # sometimes the stream_slice.get(self.slice_key) has the list of records,
        # to avoid data exposition inside the logs, we should get the data we need correctly out of stream_slice.
        if isinstance(slice_data, list) and self.nested_record_field_name is not None and len(slice_data) > 0:
            slice_data = slice_data[0].get(self.nested_record_field_name)

        # reading substream records
        self.logger.info(f"Reading {self.name} for {self.slice_key}: {slice_data}")
        records = super().read_records(stream_slice=stream_slice, **kwargs)
        # get the cached substream state, to avoid state collisions for Incremental Syncs
        cached_substream_state = stream_state_cache.cached_state.get(self.name, {})
        # filtering the portion of already emmited substream records using cached state value,
        # since the actual `metafields` endpoint doesn't support the server-side filtering using query params
        # thus to avoid the duplicates - we filter the records following the cached state,
        # which is freezed every time the sync starts using the actual STATE provided,
        # while the active STATE is updated during the sync and saved as expected, in the end.
        yield from self.filter_records_newer_than_state(stream_state=cached_substream_state, records_slice=records)


class MetafieldShopifySubstream(IncrementalShopifySubstream):
    slice_key = "id"
    data_field = "metafields"

    parent_stream_class: Union[ShopifyStream, IncrementalShopifyStream] = None

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        object_id = stream_slice[self.slice_key]
        return f"{self.parent_stream_class.data_field}/{object_id}/{self.data_field}.json"


class IncrementalShopifyNestedStream(IncrementalShopifyStream):
    """
    IncrementalShopifyNestedStream - provides slicing functionality for streams using parts of data from parent stream.

    For example:
       - `refunds` is the entity of `order.refunds`,
       - `fulfillments` is the entity of  the  `order.fulfillments` which is nested sub-entity

    ::  @ parent_stream - defines the parent stream object to read from
    ::  @ mutation_map - defines how the nested record should be populated with additional values,
          available from parent record.
          Example:
            >> mutation_map = {"parent_id": "id"},
            where `parent_id` is the new field that created for each subrecord available.
            and `id` is the parent_key named `id`, we take the value from.

    ::  @ nested_entity - the name of the nested entity inside of parent stream, helps to reduce the number of
          API Calls, if present, see `OrderRefunds` or `Fulfillments` streams for more info.
    """

    # Setting the check point interval to the limit of the records output
    state_checkpoint_interval = 100
    filter_by_state_checkpoint = True
    data_field = None
    parent_stream_class: Union[ShopifyStream, IncrementalShopifyStream] = None
    mutation_map: Mapping[str, Any] = None
    nested_entity = None

    @property
    def availability_strategy(self) -> None:
        """
        Disable Availability checks for the Nested Substreams,
        since they are dependent on the Parent Stream availability.
        """
        return None

    @cached_property
    def parent_stream(self) -> object:
        """
        Returns the instance of parent stream, if the substream has a `parent_stream_class` dependency.
        """
        return self.parent_stream_class(self.config) if self.parent_stream_class else None

    def path(self, **kwargs) -> str:
        """
        NOT USED FOR THIS TYPE OF STREAMS.
        """
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        NOT USED FOR THIS TYPE OF STREAMS.
        """
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """
        NOT USED FOR THIS TYPE OF STREAMS.
        """
        return {}

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        """UPDATING THE STATE OBJECT:
        Stream: Transactions
        Parent Stream: Orders
        Returns:
            {
                {...},
                "transactions": {
                    "created_at": "2022-03-03T03:47:45-08:00",
                    "orders": {
                        "updated_at": "2022-03-03T03:47:46-08:00"
                    }
                },
                {...},
            }
        """
        updated_state = super().get_updated_state(current_stream_state, latest_record)
        # add parent_stream_state to `updated_state`
        updated_state[self.parent_stream.name] = stream_state_cache.cached_state.get(self.parent_stream.name)
        return updated_state

    def populate_with_parent_id(self, record: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        """
        Adds new field to the record with name `key` based on the `value` key from record.
        """
        if self.mutation_map and record:
            for subrecord in record.get(self.nested_entity, []):
                for k, v in self.mutation_map.items():
                    subrecord[k] = record.get(v)
        else:
            return record

    def track_parent_stream_state(self, parent_record: Optional[Mapping[str, Any]] = None):
        # updating the `stream_state` with the state of it's parent stream
        # to have the child stream sync independently from the parent stream
        stream_state_cache.cached_state[self.parent_stream.name] = self.parent_stream.get_updated_state(
            # present state
            stream_state_cache.cached_state.get(self.parent_stream.name, {}),
            # most recent record
            parent_record if parent_record else {},
        )

    # the stream_state caching is required to avoid the STATE collisions for Substreams
    @stream_state_cache.cache_stream_state
    def stream_slices(self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_state = stream_state.get(self.parent_stream.name) if stream_state else {}
        # `sub record buffer` tunes the STATE frequency, to `checkpoint_interval`
        # for the `nested streams` with List[object], but doesn't handle List[{}] (list of one) case,
        # thus sometimes, we've got duplicated STATE with 0 records,
        # since we emit the STATE for every slice.
        nested_substream_records_buffer = []

        for parent_record in self.parent_stream.read_records(stream_state=parent_stream_state, **kwargs):
            self.track_parent_stream_state(parent_record)
            # to limit the number of API Calls and reduce the time of data fetch,
            # we can pull the ready data for child_substream, if nested data is present,
            # and corresponds to the data of child_substream we need.
            if self.nested_entity in parent_record.keys():
                # add parent_id key, value from mutation_map, if passed.
                self.populate_with_parent_id(parent_record)
                # unpack the nested list to the sub_set buffer
                nested_records = [sub_record for sub_record in parent_record.get(self.nested_entity, [])]
                # add nested_records to the buffer, with no summarization.
                nested_substream_records_buffer += nested_records
                # emit slice when there is a resonable amount of data collected,
                # to reduce the amount of STATE messages after each slice.
                if len(nested_substream_records_buffer) >= self.state_checkpoint_interval:
                    yield {self.nested_entity: nested_substream_records_buffer}
                    # clean the buffer for the next records batch
                    nested_substream_records_buffer.clear()

        # emit leftovers
        if len(nested_substream_records_buffer) > 0:
            yield {self.nested_entity: nested_substream_records_buffer}

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        # get the cached substream state, to avoid state collisions for Incremental Syncs
        cached_state = stream_state_cache.cached_state.get(self.name, {})
        # emitting nested parent entity
        yield from self.filter_records_newer_than_state(cached_state, self.produce_records(stream_slice.get(self.nested_entity, [])))


class IncrementalShopifyStreamWithDeletedEvents(IncrementalShopifyStream):
    def __init__(self, config: Dict) -> None:
        self._stream_state: MutableMapping[str, Any] = {}
        super().__init__(config)

    @property
    @abstractmethod
    def deleted_events_api_name(self) -> str:
        """
        The string value of the Shopify Events Object to pull:

            articles -> Article
            blogs -> Blog
            custom_collections -> Collection
            orders -> Order
            pages -> Page
            price_rules -> PriceRule
            products -> Product

        """

    @property
    def deleted_events(self) -> ShopifyDeletedEventsStream:
        """
        The Events stream instance to fetch the `destroyed` records for specified `deleted_events_api_name`, like: `Product`.
        See more in `ShopifyDeletedEventsStream` class.
        """
        return ShopifyDeletedEventsStream(self.config, self.deleted_events_api_name)

    @property
    def default_deleted_state_comparison_value(self) -> Union[int, str]:
        """
        Set the default STATE comparison value for cases when the deleted record doesn't have it's value.
        We expect the `deleted_at` cursor field for destroyed records would be always type of String.
        """
        return ""

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        We extend the stream state with `deleted` property to store the `destroyed` records STATE separetely from the Stream State.
        """
        self._stream_state = super().get_updated_state(self._stream_state, latest_record)
        # add `deleted` property to each stream supports `deleted events`,
        # to provide the `Incremental` sync mode, for the `Incremental Delete` records.
        last_deleted_record_value = latest_record.get(self.deleted_cursor_field) or self.default_deleted_state_comparison_value
        current_deleted_state_value = current_stream_state.get(self.deleted_cursor_field) or self.default_deleted_state_comparison_value
        self._stream_state["deleted"] = {self.deleted_cursor_field: max(last_deleted_record_value, current_deleted_state_value)}
        return self._stream_state

    def read_records(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """Override to fetch deleted records for supported streams"""
        # main records stream
        yield from super().read_records(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        # fetch deleted events after the Stream data is pulled
        yield from self.deleted_events.read_records(stream_state=stream_state, **kwargs)


class IncrementalShopifyGraphQlBulkStream(IncrementalShopifyStream):
    filter_field = "updated_at"
    cursor_field = "updated_at"
    data_field = "graphql"

    parent_stream_class: Optional[Union[ShopifyStream, IncrementalShopifyStream]] = None

    def __init__(self, config: Dict) -> None:
        super().__init__(config)
        # define BULK Manager instance
        self.job_manager: ShopifyBulkManager = ShopifyBulkManager(
            http_client=self.bulk_http_client,
            base_url=f"{self.url_base}{self.path()}",
            query=self.bulk_query(config, self.parent_stream_query_cursor_alias),
            job_termination_threshold=float(config.get("job_termination_threshold", 3600)),
            # overide the default job slice size, if provided (it's auto-adjusted, later on)
            job_size=config.get("bulk_window_in_days", 30.0),
            # provide the job checkpoint interval value, default value is 200k lines collected
            job_checkpoint_interval=config.get("job_checkpoint_interval", 200_000),
            parent_stream_name=self.parent_stream_name,
            parent_stream_cursor=self.parent_stream_cursor,
        )

    @property
    def filter_by_state_checkpoint(self) -> bool:
        return self.job_manager._supports_checkpointing

    @property
    def bulk_http_client(self) -> HttpClient:
        """
        Returns the instance of the `HttpClient`, with the stream info.
        """
        return HttpClient(self.name, self.logger, ShopifyErrorHandler(), session=self._http_client._session)

    @cached_property
    def parent_stream(self) -> Union[ShopifyStream, IncrementalShopifyStream]:
        """
        Returns the instance of parent stream, if the substream has a `parent_stream_class` dependency.
        """
        return self.parent_stream_class(self.config) if self.parent_stream_class else None

    @cached_property
    def parent_stream_name(self) -> Optional[str]:
        """
        Returns the parent stream name, if the substream has a `parent_stream_class` dependency.
        """
        return self.parent_stream.name if self.parent_stream_class else None

    @cached_property
    def parent_stream_cursor(self) -> Optional[str]:
        """
        Returns the parent stream cursor, if the substream has a `parent_stream_class` dependency.
        """
        return self.parent_stream.cursor_field if self.parent_stream_class else None

    @cached_property
    def parent_stream_query_cursor_alias(self) -> Optional[str]:
        if self.parent_stream_name and self.parent_stream_cursor:
            return f"{self.parent_stream_name}_{self.parent_stream_cursor}"

    @property
    @abstractmethod
    def bulk_query(self) -> ShopifyBulkQuery:
        """
        This method property should be defined in the stream class instance,
        and should be instantiated from the `ShopifyBulkQuery` class.
        """

    def add_shop_url_field(self, records: Iterable[MutableMapping[str, Any]] = []) -> Iterable[MutableMapping[str, Any]]:
        # ! Mandatory, add shop_url to the record to make querying easy
        # more info: https://github.com/airbytehq/airbyte/issues/25110
        for record in records:
            if record:
                record["shop_url"] = self.config["shop"]
                yield record

    @property
    def default_state_comparison_value(self) -> Union[int, str]:
        # certain streams are using `id` field as `cursor_field`, which requires to use `int` type,
        # but many other use `str` values for this, we determine what to use based on `cursor_field` value
        return 0 if self.cursor_field == "id" else self.config.get("start_date")

    # CDK OVERIDES
    @property
    def availability_strategy(self) -> None:
        """NOT USED FOR BULK OPERATIONS TO SAVE THE RATE LIMITS AND TIME FOR THE SYNC."""
        return None

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        """UPDATING THE STATE OBJECT:
        Stream: CustomerAddress
        Parent Stream: Customers
        Returns:
            {
                "customer_address": {
                    "id": 12345,
                    "customers": {
                        "updated_at": "2022-03-03T03:47:46-08:00"
                    }
                }
            }
        """

        updated_state = super().get_updated_state(current_stream_state, latest_record)

        if self.parent_stream_class:
            # the default way of getting the parent stream state is to use the value from the RecordProducer,
            # since the parent record could be present but no substream's records are present to emit,
            # the parent state is tracked for each parent record processed, thus updated regardless having substream records.
            tracked_parent_state = self.job_manager.record_producer.get_parent_stream_state()
            # fallback to the record level to search for the parent cursor or use the stream cursor value
            parent_state = tracked_parent_state if tracked_parent_state else self._get_parent_state_from_record(latest_record)
            # add parent_stream_state to `updated_state`
            updated_state[self.parent_stream_name] = parent_state

        return updated_state

    def _get_parent_state_from_record(self, latest_record: Mapping[str, Any]) -> MutableMapping[str, Any]:
        parent_state = latest_record.get(self.parent_stream_name, {})
        parent_state_value = parent_state.get(self.parent_stream_cursor) if parent_state else latest_record.get(self.parent_stream_cursor)
        parent_state[self.parent_stream_cursor] = parent_state_value
        return parent_state

    def _get_stream_cursor_value(self, stream_state: Optional[Mapping[str, Any]] = None) -> Optional[str]:
        if stream_state:
            return stream_state.get(self.cursor_field, self.default_state_comparison_value)
        else:
            return self.config.get("start_date")

    def _get_stream_state_value(self, stream_state: Optional[Mapping[str, Any]] = None) -> Optional[str]:
        if stream_state:
            if self.parent_stream_class:
                # get parent stream state from the stream_state object.
                parent_state = stream_state.get(self.parent_stream_name, {})
                if parent_state:
                    return parent_state.get(self.parent_stream_cursor, self.default_state_comparison_value)
                else:
                    # use the streams cursor value, if no parent state available
                    return self._get_stream_cursor_value(stream_state)
            else:
                # get the stream state, if no `parent_stream_class` was assigned.
                return self._get_stream_cursor_value(stream_state)
        else:
            return self.config.get("start_date")

    def _get_state_value(self, stream_state: Optional[Mapping[str, Any]] = None) -> Optional[Union[str, int]]:
        if stream_state:
            return self._get_stream_state_value(stream_state)
        else:
            # for majority of cases we fallback to start_date, otherwise.
            return self.config.get("start_date")

    def emit_slice_message(self, slice_start: datetime, slice_end: datetime) -> None:
        slice_size_message = f"Slice size: `P{round(self.job_manager._job_size, 1)}D`"
        slice_message = f"Stream: `{self.name}` requesting BULK Job for period: {slice_start} -- {slice_end}. {slice_size_message}."

        if self.job_manager._supports_checkpointing:
            checkpointing_message = f" The BULK checkpoint after `{self.job_manager.job_checkpoint_interval}` lines."
        else:
            checkpointing_message = f" The BULK checkpointing is not supported."

        self.logger.info(slice_message + checkpointing_message)

    def emit_checkpoint_message(self) -> None:
        if self.job_manager._job_adjust_slice_from_checkpoint:
            self.logger.info(f"Stream {self.name}, continue from checkpoint: `{self._checkpoint_cursor}`.")

    @stream_state_cache.cache_stream_state
    def stream_slices(self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if self.filter_field:
            state = self._get_state_value(stream_state)
            start = pdm.parse(state)
            end = pdm.now()
            while start < end:
                self.job_manager.job_size_normalize(start, end)
                slice_end = self.job_manager.get_adjusted_job_start(start)
                self.emit_slice_message(start, slice_end)
                yield {"start": start.to_rfc3339_string(), "end": slice_end.to_rfc3339_string()}
                # increment the end of the slice or reduce the next slice
                start = self.job_manager.get_adjusted_job_end(start, slice_end, self._checkpoint_cursor)
        else:
            # for the streams that don't support filtering
            yield {}

    def sort_output_asc(self, non_sorted_records: Iterable[Mapping[str, Any]] = None) -> Iterable[Mapping[str, Any]]:
        """
        Apply sorting for collected records, to guarantee the `ASC` output.
        This handles the STATE and CHECKPOINTING correctly, for the `incremental` streams.
        """
        if non_sorted_records:
            if not self.cursor_field:
                yield from non_sorted_records
            else:
                yield from sorted(
                    non_sorted_records,
                    key=lambda x: x.get(self.cursor_field) if x.get(self.cursor_field) else self.default_state_comparison_value,
                )
        else:
            # always return an empty iterable, if no records
            return []

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        self.job_manager.create_job(stream_slice, self.filter_field)
        stream_state = stream_state_cache.cached_state.get(self.name, {self.cursor_field: self.default_state_comparison_value})
        # add `shop_url` field to each record produced
        records = self.add_shop_url_field(
            # produce records from saved bulk job result
            self.job_manager.job_get_results()
        )
        # emit records in ASC order
        yield from self.filter_records_newer_than_state(stream_state, self.sort_output_asc(records))
        # add log message about the checkpoint value
        self.emit_checkpoint_message()
