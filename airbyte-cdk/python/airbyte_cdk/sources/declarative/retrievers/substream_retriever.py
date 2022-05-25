#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors.http_extractor import HttpExtractor
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.states.state import State
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http import HttpStream


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
    ):
        super().__init__(name, primary_key, requester, paginator, extractor, stream_slicer, state)
        self._parent_stream = parent_stream

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
