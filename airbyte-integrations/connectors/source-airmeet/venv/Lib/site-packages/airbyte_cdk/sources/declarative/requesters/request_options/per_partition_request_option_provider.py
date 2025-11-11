from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.partition_routers import PartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_options import RequestOptionsProvider
from airbyte_cdk.sources.types import StreamSlice, StreamState


class PerPartitionRequestOptionsProvider(RequestOptionsProvider):
    def __init__(self, partition_router: PartitionRouter, cursor_provider: RequestOptionsProvider):
        self._partition_router = partition_router
        self._cursor_provider = cursor_provider

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_params(  # type: ignore # this always returns a mapping
            stream_state=stream_state,
            stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={})
            if stream_slice
            else StreamSlice(partition={}, cursor_slice={}),
            next_page_token=next_page_token,
        ) | self._cursor_provider.get_request_params(
            stream_state=stream_state,
            stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice)
            if stream_slice
            else StreamSlice(partition={}, cursor_slice={}),
            next_page_token=next_page_token,
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_headers(  # type: ignore # this always returns a mapping
            stream_state=stream_state,
            stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={})
            if stream_slice
            else stream_slice,
            next_page_token=next_page_token,
        ) | self._cursor_provider.get_request_headers(
            stream_state=stream_state,
            stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice)
            if stream_slice
            else stream_slice,
            next_page_token=next_page_token,
        )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return self._partition_router.get_request_body_data(  # type: ignore # this always returns a mapping
            stream_state=stream_state,
            stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={})
            if stream_slice
            else stream_slice,
            next_page_token=next_page_token,
        ) | self._cursor_provider.get_request_body_data(
            stream_state=stream_state,
            stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice)
            if stream_slice
            else stream_slice,
            next_page_token=next_page_token,
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_body_json(  # type: ignore # this always returns a mapping
            stream_state=stream_state,
            stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={})
            if stream_slice
            else stream_slice,
            next_page_token=next_page_token,
        ) | self._cursor_provider.get_request_body_json(
            stream_state=stream_state,
            stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice)
            if stream_slice
            else stream_slice,
            next_page_token=next_page_token,
        )
