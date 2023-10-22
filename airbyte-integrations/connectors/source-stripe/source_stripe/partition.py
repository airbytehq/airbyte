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
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_protocol.models import SyncMode


class PaginatedRequester:
    def __init__(self, requester: Requester, record_selector: RecordSelector, paginator: DefaultPaginator):
        self._requester = requester
        self._record_selector = record_selector
        self._page_token_option = paginator.page_token_option
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
            if next_page_token:
                next_page_parameter = {self._page_token_option.field_name: next_page_token["next_page_token"]}

                if self._page_token_option.inject_into == RequestOptionType.request_parameter:
                    request_params = request_params | next_page_parameter
                elif self._page_token_option.inject_into == RequestOptionType.header:
                    request_headers = request_headers | next_page_parameter
                elif self._page_token_option.inject_into == RequestOptionType.body_data:
                    request_body_data = request_body_data | next_page_parameter
                elif self._page_token_option.inject_into == RequestOptionType.body_json:
                    request_body_json = request_body_json | next_page_parameter

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


class StripePartitionGenerator(PartitionGenerator):
    def __init__(self, stream: Stream, message_repository: MessageRepository, requester: PaginatedRequester):
        self._stream = stream
        self._message_repository = message_repository
        self._requester = requester

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        for s in self._stream.stream_slices(sync_mode=sync_mode):
            yield StripePartition(copy.deepcopy(s), self._message_repository, self._requester)


class SourcePartition(Partition):
    def __init__(self, _slice: Mapping[str, Any], message_repository: MessageRepository, requester: PaginatedRequester):
        self._slice = _slice
        self._message_repository = message_repository
        self._requester = requester

    @property
    def request_parameters(self) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def request_headers(self) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def request_body_data(self) -> Optional[Union[Mapping[str, Any], str]]:
        return None

    @property
    def request_body_json(self) -> Optional[Mapping[str, Any]]:
        return None

    def read(self) -> Iterable[Record]:
        for r in self._requester.send_requests(
            request_params=self.request_parameters,
            request_headers=self.request_headers,
            request_body_data=self.request_body_data,
            request_body_json=self.request_body_json,
        ):
            yield Record(r)

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        return hash(str(self._slice))


class StripePartition(SourcePartition):
    @property
    def request_parameters(self) -> Mapping[str, Any]:
        params = {
            "limit": 100,
            "created[gte]": self._slice.get("created[gte]") if self._slice else None,
            "created[lte]": self._slice.get("created[lte]") if self._slice else None,
        }

        return {k: v for k, v in params.items() if v}
