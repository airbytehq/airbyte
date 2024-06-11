#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from dataclasses import InitVar, dataclass, field
from functools import partial
from itertools import islice
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Union

import requests
from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.incremental import ResumableFullRefreshCursor
from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.http_logger import format_http_message
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils.mapping_helpers import combine_mappings

FULL_REFRESH_SYNC_COMPLETE_KEY = "__ab_full_refresh_sync_complete"


@dataclass
class SimpleRetriever(Retriever):
    """
    Retrieves records by synchronously sending requests to fetch records.

    The retriever acts as an orchestrator between the requester, the record selector, the paginator, and the stream slicer.

    For each stream slice, submit requests until there are no more pages of records to fetch.

    This retriever currently inherits from HttpStream to reuse the request submission and pagination machinery.
    As a result, some of the parameters passed to some methods are unused.
    The two will be decoupled in a future release.

    Attributes:
        stream_name (str): The stream's name
        stream_primary_key (Optional[Union[str, List[str], List[List[str]]]]): The stream's primary key
        requester (Requester): The HTTP requester
        record_selector (HttpSelector): The record selector
        paginator (Optional[Paginator]): The paginator
        stream_slicer (Optional[StreamSlicer]): The stream slicer
        cursor (Optional[cursor]): The cursor
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    requester: Requester
    record_selector: HttpSelector
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    name: str
    _name: Union[InterpolatedString, str] = field(init=False, repr=False, default="")
    primary_key: Optional[Union[str, List[str], List[List[str]]]]
    _primary_key: str = field(init=False, repr=False, default="")
    paginator: Optional[Paginator] = None
    stream_slicer: StreamSlicer = field(default_factory=lambda: SinglePartitionRouter(parameters={}))
    cursor: Optional[DeclarativeCursor] = None
    ignore_stream_slicer_parameters_on_paginated_requests: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._paginator = self.paginator or NoPagination(parameters=parameters)
        self._last_response: Optional[requests.Response] = None
        self._last_page_size: int = 0
        self._last_record: Optional[Record] = None
        self._parameters = parameters
        self._name = InterpolatedString(self._name, parameters=parameters) if isinstance(self._name, str) else self._name

        # This mapping is used during a resumable full refresh syncs to indicate whether a partition has started syncing
        # records. Partitions serve as the key and map to True if they already began processing records
        self._partition_started: MutableMapping[Any, bool] = dict()

    @property  # type: ignore
    def name(self) -> str:
        """
        :return: Stream name
        """
        return str(self._name.eval(self.config)) if isinstance(self._name, InterpolatedString) else self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, property):
            self._name = value

    def _get_mapping(
        self, method: Callable[..., Optional[Union[Mapping[str, Any], str]]], **kwargs: Any
    ) -> Tuple[Union[Mapping[str, Any], str], Set[str]]:
        """
        Get mapping from the provided method, and get the keys of the mapping.
        If the method returns a string, it will return the string and an empty set.
        If the method returns a dict, it will return the dict and its keys.
        """
        mapping = method(**kwargs) or {}
        keys = set(mapping.keys()) if not isinstance(mapping, str) else set()
        return mapping, keys

    def _get_request_options(
        self,
        stream_state: Optional[StreamData],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        paginator_method: Callable[..., Optional[Union[Mapping[str, Any], str]]],
        stream_slicer_method: Callable[..., Optional[Union[Mapping[str, Any], str]]],
    ) -> Union[Mapping[str, Any], str]:
        """
        Get the request_option from the paginator and the stream slicer.
        Raise a ValueError if there's a key collision
        Returned merged mapping otherwise
        """
        # FIXME we should eventually remove the usage of stream_state as part of the interpolation
        mappings = [
            paginator_method(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        ]
        if not next_page_token or not self.ignore_stream_slicer_parameters_on_paginated_requests:
            mappings.append(stream_slicer_method(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token))
        return combine_mappings(mappings)

    def _request_headers(
        self,
        stream_state: Optional[StreamData] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.
        """
        headers = self._get_request_options(
            stream_state,
            stream_slice,
            next_page_token,
            self._paginator.get_request_headers,
            self.stream_slicer.get_request_headers,
        )
        if isinstance(headers, str):
            raise ValueError("Request headers cannot be a string")
        return {str(k): str(v) for k, v in headers.items()}

    def _request_params(
        self,
        stream_state: Optional[StreamData] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        params = self._get_request_options(
            stream_state,
            stream_slice,
            next_page_token,
            self._paginator.get_request_params,
            self.stream_slicer.get_request_params,
        )
        if isinstance(params, str):
            raise ValueError("Request params cannot be a string")
        return params

    def _request_body_data(
        self,
        stream_state: Optional[StreamData] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        """
        Specifies how to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return self._get_request_options(
            stream_state,
            stream_slice,
            next_page_token,
            self._paginator.get_request_body_data,
            self.stream_slicer.get_request_body_data,
        )

    def _request_body_json(
        self,
        stream_state: Optional[StreamData] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Specifies how to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        body_json = self._get_request_options(
            stream_state,
            stream_slice,
            next_page_token,
            self._paginator.get_request_body_json,
            self.stream_slicer.get_request_body_json,
        )
        if isinstance(body_json, str):
            raise ValueError("Request body json cannot be a string")
        return body_json

    def _paginator_path(
        self,
    ) -> Optional[str]:
        """
        If the paginator points to a path, follow it, else return nothing so the requester is used.
        :param stream_state:
        :param stream_slice:
        :param next_page_token:
        :return:
        """
        return self._paginator.path()

    def _parse_response(
        self,
        response: Optional[requests.Response],
        stream_state: StreamState,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Record]:
        if not response:
            self._last_response = None
            return []

        self._last_response = response
        record_generator = self.record_selector.select_records(
            response=response,
            stream_state=stream_state,
            records_schema=records_schema,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        self._last_page_size = 0
        for record in record_generator:
            self._last_page_size += 1
            self._last_record = record
            yield record

    @property  # type: ignore
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """The stream's primary key"""
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: str) -> None:
        if not isinstance(value, property):
            self._primary_key = value

    def _next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Specifies a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        return self._paginator.next_page_token(response, self._last_page_size, self._last_record)

    def _fetch_next_page(
        self, stream_state: Mapping[str, Any], stream_slice: StreamSlice, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Optional[requests.Response]:
        return self.requester.send_request(
            path=self._paginator_path(),
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
            request_headers=self._request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            request_params=self._request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            request_body_data=self._request_body_data(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            ),
            request_body_json=self._request_body_json(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            ),
        )

    # This logic is similar to _read_pages in the HttpStream class. When making changes here, consider making changes there as well.
    def _read_pages(
        self,
        records_generator_fn: Callable[[Optional[requests.Response]], Iterable[StreamData]],
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
    ) -> Iterable[StreamData]:
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            response = self._fetch_next_page(stream_state, stream_slice, next_page_token)
            yield from records_generator_fn(response)

            if not response:
                pagination_complete = True
            else:
                next_page_token = self._next_page_token(response)
                if not next_page_token:
                    pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def _read_page(
        self,
        records_generator_fn: Callable[[Optional[requests.Response]], Iterable[StreamData]],
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
    ) -> Iterable[StreamData]:
        response = self._fetch_next_page(stream_state, stream_slice)
        yield from records_generator_fn(response)

        if not response:
            next_page_token: Mapping[str, Any] = {FULL_REFRESH_SYNC_COMPLETE_KEY: True}
        else:
            next_page_token = self._next_page_token(response) or {FULL_REFRESH_SYNC_COMPLETE_KEY: True}

        if self.cursor:
            self.cursor.close_slice(StreamSlice(cursor_slice=next_page_token, partition=stream_slice.partition))

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        """
        Fetch a stream's records from an HTTP API source

        :param records_schema: json schema to describe record
        :param stream_slice: The stream slice to read data for
        :return: The records read from the API source
        """
        _slice = stream_slice or StreamSlice(partition={}, cursor_slice={})  # None-check

        most_recent_record_from_slice = None
        record_generator = partial(
            self._parse_records,
            stream_state=self.state or {},
            stream_slice=_slice,
            records_schema=records_schema,
        )

        if self.cursor and isinstance(self.cursor, ResumableFullRefreshCursor):
            stream_state = self.state

            # Before syncing the RFR stream, we check if the job's prior attempt was successful and don't need to fetch more records
            # The platform deletes stream state for full refresh streams before starting a new job, so we don't need to worry about
            # this value existing for the initial attempt
            if stream_state.get(FULL_REFRESH_SYNC_COMPLETE_KEY):
                return
            cursor_value = stream_state.get("next_page_token")

            # The first attempt to read a page for the current partition should reset the paginator to the current
            # cursor state which is initially assigned to the incoming state from the platform
            partition_key = self._to_partition_key(_slice.partition)
            if partition_key not in self._partition_started:
                self._partition_started[partition_key] = True
                self._paginator.reset(reset_value=cursor_value)

            yield from self._read_page(record_generator, stream_state, _slice)
        else:
            # Fixing paginator types has a long tail of dependencies
            self._paginator.reset()

            for stream_data in self._read_pages(record_generator, self.state, _slice):
                current_record = self._extract_record(stream_data, _slice)
                if self.cursor and current_record:
                    self.cursor.observe(_slice, current_record)

                # Latest record read, not necessarily within slice boundaries.
                # TODO Remove once all custom components implement `observe` method.
                # https://github.com/airbytehq/airbyte-internal-issues/issues/6955
                most_recent_record_from_slice = self._get_most_recent_record(most_recent_record_from_slice, current_record, _slice)
                yield stream_data

            if self.cursor:
                self.cursor.close_slice(_slice, most_recent_record_from_slice)
        return

    def _get_most_recent_record(
        self, current_most_recent: Optional[Record], current_record: Optional[Record], stream_slice: StreamSlice
    ) -> Optional[Record]:
        if self.cursor and current_record:
            if not current_most_recent:
                return current_record
            else:
                return current_most_recent if self.cursor.is_greater_than_or_equal(current_most_recent, current_record) else current_record
        else:
            return None

    @staticmethod
    def _extract_record(stream_data: StreamData, stream_slice: StreamSlice) -> Optional[Record]:
        """
        As we allow the output of _read_pages to be StreamData, it can be multiple things. Therefore, we need to filter out and normalize
        to data to streamline the rest of the process.
        """
        if isinstance(stream_data, Record):
            # Record is not part of `StreamData` but is the most common implementation of `Mapping[str, Any]` which is part of `StreamData`
            return stream_data
        elif isinstance(stream_data, (dict, Mapping)):
            return Record(dict(stream_data), stream_slice)
        elif isinstance(stream_data, AirbyteMessage) and stream_data.record:
            return Record(stream_data.record.data, stream_slice)
        return None

    # stream_slices is defined with arguments on http stream and fixing this has a long tail of dependencies. Will be resolved by the decoupling of http stream and simple retriever
    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:  # type: ignore
        """
        Specifies the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        return self.stream_slicer.stream_slices()

    @property
    def state(self) -> Mapping[str, Any]:
        return self.cursor.get_stream_state() if self.cursor else {}

    @state.setter
    def state(self, value: StreamState) -> None:
        """State setter, accept state serialized by state getter."""
        if self.cursor:
            self.cursor.set_initial_state(value)

    def _parse_records(
        self,
        response: Optional[requests.Response],
        stream_state: Mapping[str, Any],
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice],
    ) -> Iterable[StreamData]:
        yield from self._parse_response(
            response,
            stream_slice=stream_slice,
            stream_state=stream_state,
            records_schema=records_schema,
        )

    def must_deduplicate_query_params(self) -> bool:
        return True

    @staticmethod
    def _to_partition_key(to_serialize: Any) -> str:
        # separators have changed in Python 3.4. To avoid being impacted by further change, we explicitly specify our own value
        return json.dumps(to_serialize, indent=None, separators=(",", ":"), sort_keys=True)


@dataclass
class SimpleRetrieverTestReadDecorator(SimpleRetriever):
    """
    In some cases, we want to limit the number of requests that are made to the backend source. This class allows for limiting the number of
    slices that are queried throughout a read command.
    """

    maximum_number_of_slices: int = 5

    def __post_init__(self, options: Mapping[str, Any]) -> None:
        super().__post_init__(options)
        if self.maximum_number_of_slices and self.maximum_number_of_slices < 1:
            raise ValueError(
                f"The maximum number of slices on a test read needs to be strictly positive. Got {self.maximum_number_of_slices}"
            )

    # stream_slices is defined with arguments on http stream and fixing this has a long tail of dependencies. Will be resolved by the decoupling of http stream and simple retriever
    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:  # type: ignore
        return islice(super().stream_slices(), self.maximum_number_of_slices)

    def _fetch_next_page(
        self, stream_state: Mapping[str, Any], stream_slice: StreamSlice, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Optional[requests.Response]:
        return self.requester.send_request(
            path=self._paginator_path(),
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
            request_headers=self._request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            request_params=self._request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            request_body_data=self._request_body_data(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            ),
            request_body_json=self._request_body_json(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            ),
            log_formatter=lambda response: format_http_message(
                response,
                f"Stream '{self.name}' request",
                f"Request performed in order to extract records for stream '{self.name}'",
                self.name,
            ),
        )
