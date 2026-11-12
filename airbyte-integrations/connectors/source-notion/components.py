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
# key holding the global cursor value in the state of a `global_substream_cursor` stream
_GLOBAL_STATE_KEY = "state"
logger = logging.getLogger("airbyte")


@dataclass
class BlocksRetriever(SimpleRetriever):
    """
    Docs: https://developers.notion.com/reference/get-block-children

    According to that fact that block's entity may have children entities that stream also need to retrieve
    BlocksRetriever calls read_records when received record.has_children is True.

    Client-side incremental filtering: the CDK only wires `is_client_side_incremental` into the record selector of
    built-in retrievers, so for this custom retriever the stream cursor is received here and records are filtered
    against it after the block tree has been walked. Filtering has to happen after the traversal (not in the record
    selector) because a parent block's `last_edited_time` is not guaranteed to change when only one of its
    children changes; dropping the parent before recursing would silently skip its edited children.

    Records are only filtered when the sync starts from a saved cursor value. Full refresh and first incremental
    syncs keep emitting every block of the selected pages, including blocks last edited before `start_date`.
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
        filter_on_state = self._has_saved_cursor_value()
        for stream_data in self._read_block_tree(records_schema, stream_slice):
            if not filter_on_state or self._should_be_synced(stream_data, stream_slice):
                yield stream_data

    def _has_saved_cursor_value(self) -> bool:
        if not (self.is_client_side_incremental_sync and self.cursor):
            return False
        # The global cursor value only moves forward once the whole stream has completed, so it is the state the
        # sync started from for as long as partitions are being read.
        return bool(self.cursor.state.get(_GLOBAL_STATE_KEY))

    def _should_be_synced(self, stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        if not isinstance(stream_data, Record):
            return True
        # Child blocks are read with a synthetic `block_id` partition the cursor does not know about, so the record
        # is evaluated against the page partition that produced it.
        record = Record(data=stream_data.data, stream_name=stream_data.stream_name, associated_slice=stream_slice)
        return self.cursor.should_be_synced(record)

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
