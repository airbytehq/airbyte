#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.states.dict_state import DictState
from airbyte_cdk.sources.declarative.states.state import State
from airbyte_cdk.sources.declarative.stream_slicers.single_slice import SingleSlice
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.http import HttpStream


class SimpleRetriever(Retriever, HttpStream):
    def __init__(
        self,
        name,
        primary_key,
        requester: Requester,
        paginator: Paginator,
        record_selector: HttpSelector,
        stream_slicer: Optional[StreamSlicer] = SingleSlice,
        state: Optional[State] = None,
    ):
        self._name = name
        self._primary_key = primary_key
        self._paginator = paginator
        self._requester = requester
        self._record_selector = record_selector
        super().__init__(self._requester.get_authenticator())
        self._iterator: StreamSlicer = stream_slicer
        self._state: State = (state or DictState()).deep_copy()
        self._last_response = None
        self._last_records = None

    @property
    def name(self) -> str:
        """
        :return: Stream name
        """
        return self._name

    @property
    def url_base(self) -> str:
        return self._requester.get_url_base()

    @property
    def http_method(self) -> str:
        return str(self._requester.get_method().value)

    @property
    def raise_on_http_errors(self) -> bool:
        """
        If set to False, allows opting-out of raising HTTP code exception.
        """
        return self._requester.raise_on_http_errors

    @property
    def max_retries(self) -> Union[int, None]:
        """
        Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        return self._requester.max_retries

    @property
    def retry_factor(self) -> float:
        """
        Specifies factor to multiply the exponentiation by for backoff policy.
        """
        return self._requester.retry_factor

    def should_retry(self, response: requests.Response) -> bool:
        """
        Specifies conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        return self._requester.should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Specifies backoff time.

         This method is called only if should_backoff() returns True for the input request.

         :param response:
         :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
         to the default backoff behavior (e.g using an exponential algorithm).
        """
        return self._requester.backoff_time(response)

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return self._requester.request_headers(stream_state, stream_slice, next_page_token)

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        """
        Specifies how to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return self._requester.request_body_data(stream_state, stream_slice, next_page_token)

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        """
        Specifies how to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return self._requester.request_body_json(stream_state, stream_slice, next_page_token)

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies how to configure a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..
        """
        return self._requester.request_kwargs(stream_state, stream_slice, next_page_token)

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self._requester.get_path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        return self._requester.request_params(stream_state, stream_slice, next_page_token)

    @property
    def cache_filename(self):
        """
        Return the name of cache file
        """
        return self._requester.cache_filename

    @property
    def use_cache(self):
        """
        If True, all records will be cached.
        """
        return self._requester.use_cache

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        self._last_response = response
        records = self._record_selector.select_records(
            response=response, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )
        self._last_records = records
        return records

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Specifies a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        return self._paginator.next_page_token(response, self._last_records)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        records_generator = HttpStream.read_records(self, sync_mode, cursor_field, stream_slice, stream_state)
        for r in records_generator:
            self._state.update_state(stream_slice=stream_slice, stream_state=stream_state, last_response=self._last_response, last_record=r)
            yield r
        else:
            self._state.update_state(
                stream_slice=stream_slice, stream_state=stream_state, last_reponse=self._last_response, last_record=None
            )
            yield from []

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Specifies the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        # FIXME: this is not passing the cursor field because it is always known at init time
        return self._iterator.stream_slices(sync_mode, stream_state)

    def get_state(self) -> MutableMapping[str, Any]:
        return self._state.get_stream_state()
