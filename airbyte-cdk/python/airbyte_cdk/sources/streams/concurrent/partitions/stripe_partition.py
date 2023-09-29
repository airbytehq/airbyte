import copy
import traceback
from typing import Optional, Mapping, Any, Iterable, Union, Callable

from airbyte_protocol.models import SyncMode

import airbyte_cdk
from airbyte_cdk.sources.declarative.extractors import RecordSelector, DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.models import CursorPagination
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.paginators import Paginator, DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.types import StreamState, StreamSlice
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
import requests


class StripeLegacyPartitionGenerator(PartitionGenerator):
    def __init__(self, stream: Stream, message_repository: MessageRepository, requester):
        self._stream = stream
        self._message_repository = message_repository
        self._requester = requester

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        for s in self._stream.stream_slices(sync_mode=sync_mode):
            yield StripePartition(copy.deepcopy(s), self._message_repository, self._requester)


class PaginatedRequester:
    def __init__(self, requester, record_selector, paginator: Paginator):
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
            log_formatter: Optional[Callable[[requests.Response], Any]] = None) -> Iterable[Mapping]:
        #FIXME: the typing isn't quite right. technically this is returning a Declartive.Record

        next_page_token = None
        pagination_complete = False
        while not pagination_complete:
            if next_page_token: #also need to check the request option type...
                request_params = {**request_params, **{self._page_token_option.field_name: next_page_token["next_page_token"]}}
            response = self._requester.send_request(path=path, request_headers=request_headers, request_params=request_params,
                                                    request_body_data=request_body_data, request_body_json=request_body_json,
                                                    next_page_token=next_page_token,
                                                    log_formatter=log_formatter)
            if not response:
                pagination_complete = True
            else:
                record_data = self._record_selector.select_records(response, {})
                records = list(record_data) # This is not great...
                for record in records:
                    yield record
                next_page_token = self._paginator.next_page_token(response, records)
                print(f"next_page_token: {next_page_token}")
                if not next_page_token:
                    pagination_complete = True

class StripePartition(Partition):
    def __init__(self, _slice: Mapping[str, Any], message_repository: MessageRepository, requester):
        self._slice = _slice
        self._message_repository = message_repository
        self._requester = requester

    def read(self) -> Iterable[Record]:
        # FIXME: not all parameters should be hardcoded here...
        # Pagination should be handled somewhere...
        # need to fix the authenticator
        # Ideally don't need to pass the stream lol
        try:
            request_parameters = {"limit": "100",
                                  "created[gte]": self._slice["created[gte]"],
                                  "created[lte]": self._slice["created[lte]"]
                                  }
            for r in self._requester.send_requests(request_params=request_parameters):
                yield Record(r)

        except Exception as e:
            traceback.print_exc()
            print(e)
            exit()

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        return hash(str(self._slice))
