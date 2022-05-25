#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from itertools import chain
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors.http_extractor import HttpExtractor
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.states.state import State
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.core import Stream


class SubstreamRetriever(SimpleRetriever):
    def __init__(
        self,
        name,
        primary_key,
        requester: Requester,
        paginator: Paginator,
        extractor: HttpExtractor,
        stream_slicer: StreamSlicer,
        state: State,
        parent_stream: Stream,
        parent_extractor: HttpExtractor,
    ):
        super().__init__(name, primary_key, requester, paginator, extractor, stream_slicer, state)
        self._parent_stream = parent_stream
        self._parent_extractor = parent_extractor

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for parent_record in self._parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            # print(f"parent_record: {parent_record}")
            has_more = parent_record["lines"]
            print(has_more)
            exit()
            records = self._parent_extractor.extract_records(parent_record)
            # print(f"found {len(records)} records. first is: {records[0]['id']}")
            # print(f"stream_slice: {stream_slice}")
            next_page_token = self._paginator.next_page_token(parent_record, records)
            # print(f"next_page_token: {next_page_token}")
            if next_page_token:
                next_pages = [p for p in super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)]
                print(f"next_pages: {len(next_pages)}")
            else:
                next_pages = []

            for rec in chain(records, next_pages):
                yield rec
