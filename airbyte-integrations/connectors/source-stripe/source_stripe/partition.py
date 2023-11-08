#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from typing import Any, Callable, Iterable, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.extractors import RecordSelector
from airbyte_cdk.sources.declarative.requesters import Requester
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.utils.transform import TypeTransformer
from airbyte_protocol.models import SyncMode


class PaginatedRequester:
    def __init__(self, requester: Requester, record_selector: RecordSelector, paginator: DefaultPaginator):
        self._requester = requester
        self._record_selector = record_selector
        self._paginator = paginator

    def send_requests(
        self,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Iterable[Mapping]:
        next_page_token = None
        pagination_complete = False
        while not pagination_complete:
            additional_parameters = {self._paginator.page_size_option.field_name: self._paginator.pagination_strategy.get_page_size()}
            if next_page_token:
                additional_parameters[self._paginator.page_token_option.field_name] = next_page_token["next_page_token"]

            if self._paginator.page_token_option.inject_into == RequestOptionType.request_parameter:
                request_params = request_params | additional_parameters
            elif self._paginator.page_token_option.inject_into == RequestOptionType.header:
                request_headers = request_headers | additional_parameters
            elif self._paginator.page_token_option.inject_into == RequestOptionType.body_data:
                request_body_data = request_body_data | additional_parameters
            elif self._paginator.page_token_option.inject_into == RequestOptionType.body_json:
                request_body_json = request_body_json | additional_parameters

            response = self._requester.send_request(
                path=path,
                request_headers=request_headers,
                request_params=request_params,
                request_body_data=request_body_data,
                request_body_json=request_body_json,
                next_page_token=next_page_token,
                log_formatter=log_formatter,
            )
            if not response:
                pagination_complete = True
            else:
                records = list(self._record_selector.select_records(response, {}))
                yield from records

                next_page_token = self._paginator.next_page_token(response, records)
                if not next_page_token:
                    pagination_complete = True


class SourcePartitionGenerator(PartitionGenerator):
    def __init__(
        self,
        stream: Stream,
        requester: PaginatedRequester,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
    ):
        self._stream = stream
        self._requester = requester
        self._request_headers = request_headers
        self._request_params = request_params
        self._request_body_data = request_body_data
        self._request_body_json = request_body_json

    def generate(self) -> Iterable[Partition]:
        for s in self._stream.stream_slices(sync_mode=SyncMode.full_refresh):
            yield SourcePartition(
                copy.deepcopy(s),
                transformer=self._stream.transformer,
                json_schema=self._stream.get_json_schema(),
                requester=self._requester,
                request_headers=self._request_headers,
                request_params=self._request_params,
                request_body_data=self._request_body_data,
                request_body_json=self._request_body_json,
            )


class SourcePartition(Partition):
    def __init__(
        self,
        _slice: Mapping[str, Any],
        transformer: TypeTransformer,
        json_schema: Mapping[str, Any],
        requester: PaginatedRequester,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
    ):
        self._slice = _slice
        self._transformer = transformer
        self._json_schema = json_schema
        self._requester = requester
        self._request_headers = request_headers
        self._request_params = request_params
        self._request_body_data = request_body_data
        self._request_body_json = request_body_json

    def read(self) -> Iterable[Record]:
        for record in self._requester.send_requests(
            request_params=self._parse_request_arguments(self._request_params),
            request_headers=self._parse_request_arguments(self._request_headers),
            request_body_data=self._parse_request_arguments(self._request_body_data),
            request_body_json=self._parse_request_arguments(self._request_body_json),
        ):
            record_data = dict(record)
            self._transformer.transform(record_data, self._json_schema)
            yield Record(record_data)

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def _parse_request_arguments(self, request_arguments: Optional[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        if request_arguments is None:
            return request_arguments

        return {key: value(self._slice) for key, value in request_arguments.items() if value(self._slice)}

    def __hash__(self) -> int:
        return hash(str(self._slice))
