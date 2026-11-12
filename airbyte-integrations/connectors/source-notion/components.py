# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import ClientSideIncrementalRecordFilterDecorator, RecordFilter
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.core import StreamData


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30
logger = logging.getLogger("airbyte")


@dataclass
class BlocksRetriever(SimpleRetriever):
    """
    Docs: https://developers.notion.com/reference/get-block-children

    According to that fact that block's entity may have children entities that stream also need to retrieve
    BlocksRetriever calls read_records when received record.has_children is True.

    Client-side incremental filtering: the CDK only installs its `ClientSideIncrementalRecordFilterDecorator` on the
    record selector of a declarative `SimpleRetriever`, so a `CustomRetriever` receives the stream cursor but no
    filter. Filtering in the record selector would also be wrong for this stream: it would drop a parent block that
    was not edited since the last sync before this retriever could recurse into its children, losing child blocks
    that were edited. The retriever therefore walks the full block tree and drops the already-synced blocks itself,
    after the recursion decision has been made. If a CDK version does install the client-side filter on the record
    selector, it is moved out of the selector and applied here instead (the `record_filter` condition is kept).
    """

    # Populated by the declarative component factory from the stream's `incremental_sync` definition. `cursor` is only
    # read here, never reassigned: older CDK versions define a `cursor` field on `SimpleRetriever` with another meaning.
    cursor: Optional[Cursor] = None
    is_client_side_incremental_sync: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        self._client_side_cursor: Optional[Cursor] = self.cursor if self.is_client_side_incremental_sync else None
        self._move_client_side_filter_out_of_record_selector()

    def _move_client_side_filter_out_of_record_selector(self) -> None:
        record_filter = getattr(self.record_selector, "record_filter", None)
        if not isinstance(record_filter, ClientSideIncrementalRecordFilterDecorator):
            return
        self._client_side_cursor = self._client_side_cursor or record_filter._cursor
        self.record_selector.record_filter = (
            RecordFilter(parameters={}, config=record_filter.config, condition=record_filter.condition) if record_filter.condition else None
        )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        for stream_data in self._read_block_tree(records_schema, stream_slice):
            if self._should_be_synced(stream_data, stream_slice):
                yield stream_data

    def _should_be_synced(self, stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        if self._client_side_cursor is None or not isinstance(stream_data, Record):
            return True
        # Nested blocks are fetched with a child slice whose partition is not known to the stream cursor, so the check
        # is made against the slice that was handed to this retriever by the stream (the parent page partition).
        return self._client_side_cursor.should_be_synced(
            Record(
                data=stream_data.data, stream_name=stream_data.stream_name, associated_slice=stream_slice or stream_data.associated_slice
            )
        )

    def _read_block_tree(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        # if reached recursive limit, don't read anymore
        if self.current_block_depth > MAX_BLOCK_DEPTH:
            logger.info("Reached max block depth limit. Exiting.")
            return

        for sequence_number, stream_data in enumerate(super().read_records(records_schema, stream_slice)):
            if stream_data.data.get("has_children"):
                self.current_block_depth += 1
                child_stream_slice = StreamSlice(
                    partition={"block_id": stream_data.data["id"], "parent_slice": {}},
                    cursor_slice=stream_slice.cursor_slice,
                )
                yield from self._read_block_tree(records_schema, child_stream_slice)
                self.current_block_depth -= 1

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            yield stream_data
