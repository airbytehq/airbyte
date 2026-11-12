# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

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

    The CDK only applies client-side incremental filtering to the record selector of a `SimpleRetriever`, so a
    custom retriever has to filter on the stream's cursor itself. Once a sync has a saved checkpoint, blocks last
    edited before it are dropped. Filtering happens after the recursion decision so that recently edited children
    of an unchanged parent block are still read.
    """

    cursor: Optional[Cursor] = None
    is_client_side_incremental_sync: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        if not self._has_incremental_checkpoint():
            yield from self._read_blocks(records_schema, stream_slice)
            return

        for stream_data in self._read_blocks(records_schema, stream_slice):
            if self._should_be_synced(stream_data, stream_slice):
                yield stream_data

    def _read_blocks(
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
                yield from self._read_blocks(records_schema, child_stream_slice)
                self.current_block_depth -= 1

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            yield stream_data

    def _has_incremental_checkpoint(self) -> bool:
        # Without a saved checkpoint every block is emitted, as before, so full refresh and first syncs keep blocks
        # last edited before the start date.
        if not (self.is_client_side_incremental_sync and self.cursor):
            return False
        state = self.cursor.state
        return bool(state.get("state") or state.get("states"))

    def _should_be_synced(self, stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        if not (self.is_client_side_incremental_sync and self.cursor and isinstance(stream_data, Mapping)):
            return True
        data = stream_data.data if isinstance(stream_data, Record) else stream_data
        # Children are read against their own block slice, but the cursor only knows the partition being read.
        return self.cursor.should_be_synced(Record(data=data, stream_name=self.name, associated_slice=stream_slice))
