#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import urljoin

import requests
from airbyte_cdk.models import AirbyteMessage, FailureType, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.checkpoint.cursor import Cursor
from airbyte_cdk.sources.streams.checkpoint.resumable_full_refresh_cursor import ResumableFullRefreshCursor
from airbyte_cdk.sources.streams.checkpoint.substream_resumable_full_refresh_cursor import SubstreamResumableFullRefreshCursor
from airbyte_cdk.sources.streams.core import CheckpointMixin, Stream, StreamData
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy, ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction
from airbyte_cdk.sources.streams.http.http_client import HttpClient
from airbyte_cdk.sources.types import Record, StreamSlice
from airbyte_cdk.sources.utils.types import JsonType
from deprecated import deprecated
from requests.auth import AuthBase

# list of all possible HTTP methods which can be used for sending of request bodies
BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")


class HttpStream(Stream, CheckpointMixin, ABC):
    """
    Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.
    """

    source_defined_cursor = True  # Most HTTP streams use a source defined cursor (i.e: the user can't configure it like on a SQL table)
    page_size: Optional[int] = None  # Use this variable to define page size for API http requests with pagination support

    def __init__(self, authenticator: Optional[AuthBase] = None, api_budget: Optional[APIBudget] = None):
        self._exit_on_rate_limit: bool = False
        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.get_error_handler(),
            api_budget=api_budget or APIBudget(policies=[]),
            authenticator=authenticator,
            use_cache=self.use_cache,
            backoff_strategy=self.get_backoff_strategy(),
            message_repository=InMemoryMessageRepository(),
        )

        # There are three conditions that dictate if RFR should automatically be applied to a stream
        # 1. Streams that explicitly initialize their own cursor should defer to it and not automatically apply RFR
        # 2. Streams with at least one cursor_field are incremental and thus a superior sync to RFR.
        # 3. Streams overriding read_records() do not guarantee that they will call the parent implementation which can perform
        #    per-page checkpointing so RFR is only supported if a stream use the default `HttpStream.read_records()` method
        if not self.cursor and len(self.cursor_field) == 0 and type(self).read_records is HttpStream.read_records:
            self.cursor = ResumableFullRefreshCursor()

    @property
    def exit_on_rate_limit(self) -> bool:
        """
        :return: False if the stream will retry endlessly when rate limited
        """
        return self._exit_on_rate_limit

    @exit_on_rate_limit.setter
    def exit_on_rate_limit(self, value: bool) -> None:
        self._exit_on_rate_limit = value

    @property
    def cache_filename(self) -> str:
        """
        Override if needed. Return the name of cache file
        Note that if the environment variable REQUEST_CACHE_PATH is not set, the cache will be in-memory only.
        """
        return f"{self.name}.sqlite"

    @property
    def use_cache(self) -> bool:
        """
        Override if needed. If True, all records will be cached.
        Note that if the environment variable REQUEST_CACHE_PATH is not set, the cache will be in-memory only.
        """
        return False

    @property
    @abstractmethod
    def url_base(self) -> str:
        """
        :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"
        """

    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "GET"

    @property
    @deprecated(version="3.0.0", reason="You should set error_handler explicitly in HttpStream.get_error_handler() instead.")
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return True

    @property
    @deprecated(version="3.0.0", reason="You should set backoff_strategies explicitly in HttpStream.get_backoff_strategy() instead.")
    def max_retries(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        return 5

    @property
    @deprecated(version="3.0.0", reason="You should set backoff_strategies explicitly in HttpStream.get_backoff_strategy() instead.")
    def max_time(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum total waiting time (in seconds) for backoff policy. Return None for no limit.
        """
        return 60 * 10

    @property
    @deprecated(version="3.0.0", reason="You should set backoff_strategies explicitly in HttpStream.get_backoff_strategy() instead.")
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for backoff policy.
        """
        return 5

    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """

    @abstractmethod
    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        return {}

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {}

    def request_body_data(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Union[Mapping[str, Any], str]]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return None

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return None

    def request_kwargs(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Override to return a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..
        """
        return {}

    @abstractmethod
    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Parses the raw response object into a list of records.
        By default, this returns an iterable containing the input. Override to parse differently.
        :param response:
        :param stream_state:
        :param stream_slice:
        :param next_page_token:
        :return: An iterable containing the parsed response
        """

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        """
        Used to initialize Adapter to avoid breaking changes.
        If Stream has a `backoff_time` method implementation, we know this stream uses old (pre-HTTPClient) backoff handlers and thus an adapter is needed.

        Override to provide custom BackoffStrategy
        :return Optional[BackoffStrategy]:
        """
        if hasattr(self, "backoff_time"):
            return HttpStreamAdapterBackoffStrategy(self)
        else:
            return None

    def get_error_handler(self) -> Optional[ErrorHandler]:
        """
        Used to initialize Adapter to avoid breaking changes.
        If Stream has a `should_retry` method implementation, we know this stream uses old (pre-HTTPClient) error handlers and thus an adapter is needed.

        Override to provide custom ErrorHandler
        :return Optional[ErrorHandler]:
        """
        if hasattr(self, "should_retry"):
            error_handler = HttpStreamAdapterHttpStatusErrorHandler(
                stream=self, logger=logging.getLogger(), max_retries=self.max_retries, max_time=timedelta(seconds=self.max_time or 0)
            )
            return error_handler
        else:
            return None

    @classmethod
    def _join_url(cls, url_base: str, path: str) -> str:
        return urljoin(url_base, path)

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """

        # default logic to grab error from common fields
        def _try_get_error(value: Optional[JsonType]) -> Optional[str]:
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                errors_in_value = [_try_get_error(v) for v in value]
                return ", ".join(v for v in errors_in_value if v is not None)
            elif isinstance(value, dict):
                new_value = (
                    value.get("message")
                    or value.get("messages")
                    or value.get("error")
                    or value.get("errors")
                    or value.get("failures")
                    or value.get("failure")
                    or value.get("detail")
                )
                return _try_get_error(new_value)
            return None

        try:
            body = response.json()
            return _try_get_error(body)
        except requests.exceptions.JSONDecodeError:
            return None

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method only handles HTTPErrors by passing the response to self.parse_response_error_message().
        The method should be overriden as needed to handle any additional exception types.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        if isinstance(exception, requests.HTTPError) and exception.response is not None:
            return self.parse_response_error_message(exception.response)
        return None

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        # A cursor_field indicates this is an incremental stream which offers better checkpointing than RFR enabled via the cursor
        if self.cursor_field or not isinstance(self.get_cursor(), ResumableFullRefreshCursor):
            yield from self._read_pages(
                lambda req, res, state, _slice: self.parse_response(res, stream_slice=_slice, stream_state=state),
                stream_slice,
                stream_state,
            )
        else:
            yield from self._read_single_page(
                lambda req, res, state, _slice: self.parse_response(res, stream_slice=_slice, stream_state=state),
                stream_slice,
                stream_state,
            )

    @property
    def state(self) -> MutableMapping[str, Any]:
        cursor = self.get_cursor()
        if cursor:
            return cursor.get_stream_state()  # type: ignore
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        cursor = self.get_cursor()
        if cursor:
            cursor.set_initial_state(value)
        self._state = value

    def get_cursor(self) -> Optional[Cursor]:
        # I don't love that this is semi-stateful but not sure what else to do. We don't know exactly what type of cursor to
        # instantiate when creating the class. We can make a few assumptions like if there is a cursor_field which implies
        # incremental, but we don't know until runtime if this is a substream. Ideally, a stream should explicitly define
        # its cursor, but because we're trying to automatically apply RFR we're stuck with this logic where we replace the
        # cursor at runtime once we detect this is a substream based on self.has_multiple_slices being reassigned
        if self.has_multiple_slices and isinstance(self.cursor, ResumableFullRefreshCursor):
            self.cursor = SubstreamResumableFullRefreshCursor()
            return self.cursor
        else:
            return self.cursor

    def _read_pages(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Optional[Mapping[str, Any]]], Iterable[StreamData]
        ],
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        partition, _, _ = self._extract_slice_fields(stream_slice=stream_slice)

        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            request, response = self._fetch_next_page(stream_slice, stream_state, next_page_token)
            yield from records_generator_fn(request, response, stream_state, stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        cursor = self.get_cursor()
        if cursor and isinstance(cursor, SubstreamResumableFullRefreshCursor):
            # Substreams checkpoint state by marking an entire parent partition as completed so that on the subsequent attempt
            # after a failure, completed parents are skipped and the sync can make progress
            cursor.close_slice(StreamSlice(cursor_slice={}, partition=partition))

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def _read_single_page(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Optional[Mapping[str, Any]]], Iterable[StreamData]
        ],
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        partition, cursor_slice, remaining_slice = self._extract_slice_fields(stream_slice=stream_slice)
        stream_state = stream_state or {}
        next_page_token = cursor_slice or None

        request, response = self._fetch_next_page(remaining_slice, stream_state, next_page_token)
        yield from records_generator_fn(request, response, stream_state, remaining_slice)

        next_page_token = self.next_page_token(response) or {"__ab_full_refresh_sync_complete": True}

        cursor = self.get_cursor()
        if cursor:
            cursor.close_slice(StreamSlice(cursor_slice=next_page_token, partition=partition))

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    @staticmethod
    def _extract_slice_fields(stream_slice: Optional[Mapping[str, Any]]) -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
        if not stream_slice:
            return {}, {}, {}

        if isinstance(stream_slice, StreamSlice):
            partition = stream_slice.partition
            cursor_slice = stream_slice.cursor_slice
            remaining = {k: v for k, v in stream_slice.items()}
        else:
            # RFR streams that implement stream_slices() to generate stream slices in the legacy mapping format are converted into a
            # structured stream slice mapping by the LegacyCursorBasedCheckpointReader. The structured mapping object has separate
            # fields for the partition and cursor_slice value
            partition = stream_slice.get("partition", {})
            cursor_slice = stream_slice.get("cursor_slice", {})
            remaining = {key: val for key, val in stream_slice.items() if key != "partition" and key != "cursor_slice"}
        return partition, cursor_slice, remaining

    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:

        request, response = self._http_client.send_request(
            http_method=self.http_method,
            url=self._join_url(
                self.url_base,
                self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            ),
            request_kwargs=self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            dedupe_query_params=True,
            log_formatter=self.get_log_formatter(),
            exit_on_rate_limit=self.exit_on_rate_limit,
        )

        return request, response

    def get_log_formatter(self) -> Optional[Callable[[requests.Response], Any]]:
        """

        :return Optional[Callable[[requests.Response], Any]]: Function that will be used in logging inside HttpClient
        """
        return None


class HttpSubStream(HttpStream, ABC):
    def __init__(self, parent: HttpStream, **kwargs: Any):
        """
        :param parent: should be the instance of HttpStream class
        """
        super().__init__(**kwargs)
        self.parent = parent
        self.has_multiple_slices = True  # Substreams are based on parent records which implies there are multiple slices

        # There are three conditions that dictate if RFR should automatically be applied to a stream
        # 1. Streams that explicitly initialize their own cursor should defer to it and not automatically apply RFR
        # 2. Streams with at least one cursor_field are incremental and thus a superior sync to RFR.
        # 3. Streams overriding read_records() do not guarantee that they will call the parent implementation which can perform
        #    per-page checkpointing so RFR is only supported if a stream use the default `HttpStream.read_records()` method
        if not self.cursor and len(self.cursor_field) == 0 and type(self).read_records is HttpStream.read_records:
            self.cursor = SubstreamResumableFullRefreshCursor()

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # read_stateless() assumes the parent is not concurrent. This is currently okay since the concurrent CDK does
        # not support either substreams or RFR, but something that needs to be considered once we do
        for parent_record in self.parent.read_only_records(stream_state):
            # Skip non-records (eg AirbyteLogMessage)
            if isinstance(parent_record, AirbyteMessage):
                if parent_record.type == MessageType.RECORD:
                    parent_record = parent_record.record.data
                else:
                    continue
            elif isinstance(parent_record, Record):
                parent_record = parent_record.data
            yield {"parent": parent_record}


@deprecated(version="3.0.0", reason="You should set backoff_strategies explicitly in HttpStream.get_backoff_strategy() instead.")
class HttpStreamAdapterBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream):
        self.stream = stream

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        return self.stream.backoff_time(response_or_exception)  # type: ignore # noqa  # HttpStream.backoff_time has been deprecated


@deprecated(version="3.0.0", reason="You should set error_handler explicitly in HttpStream.get_error_handler() instead.")
class HttpStreamAdapterHttpStatusErrorHandler(HttpStatusErrorHandler):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, Exception):
            return super().interpret_response(response_or_exception)
        elif isinstance(response_or_exception, requests.Response):
            should_retry = self.stream.should_retry(response_or_exception)  # type: ignore # noqa
            if should_retry:
                if response_or_exception.status_code == 429:
                    return ErrorResolution(
                        response_action=ResponseAction.RATE_LIMITED,
                        failure_type=FailureType.transient_error,
                        error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                    )
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                )
            else:
                if response_or_exception.ok:  # type: ignore # noqa
                    return ErrorResolution(
                        response_action=ResponseAction.SUCCESS,
                        failure_type=None,
                        error_message=None,
                    )
                if self.stream.raise_on_http_errors:
                    return ErrorResolution(
                        response_action=ResponseAction.FAIL,
                        failure_type=FailureType.transient_error,
                        error_message=f"Response status code: {response_or_exception.status_code}. Unexpected error. Failed.",  # type: ignore[union-attr]
                    )
                else:
                    return ErrorResolution(
                        response_action=ResponseAction.IGNORE,
                        failure_type=FailureType.transient_error,
                        error_message=f"Response status code: {response_or_exception.status_code}. Ignoring...",  # type: ignore[union-attr]
                    )
        else:
            self._logger.error(f"Received unexpected response type: {type(response_or_exception)}")
            return ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.system_error,
                error_message=f"Received unexpected response type: {type(response_or_exception)}",
            )
