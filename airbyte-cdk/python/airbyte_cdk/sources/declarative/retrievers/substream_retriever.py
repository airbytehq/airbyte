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
        parent_records = [r for r in self._parent_stream.read_records(SyncMode.full_refresh)]
        for parent_record in parent_records:

            items_obj = parent_record.get("lines", {})
            if not items_obj:
                continue

            items = items_obj.get("data", [])
            # get next pages
            items_next_pages = []
            if items_obj.get("has_more") and items:
                print("hasmore!")
                exit()
                # stream_slice = {self.parent_id: record["id"], "starting_after": items[-1]["id"]}
                # items_next_pages = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, **kwargs)

            for item in chain(items, items_next_pages):
                yield item
        # yield from super(SubstreamRetriever, self).read_records(sync_mode, cursor_field, stream_slice, stream_state)
