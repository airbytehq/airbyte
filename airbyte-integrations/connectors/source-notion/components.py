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

    """

    # The stream's cursor. The CDK passes it to the retriever, but only wires the client-side incremental filter into
    # the record selector of a plain SimpleRetriever, so this retriever has to apply it itself.
    cursor: Optional[Cursor] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        """
        Walks the whole block tree of the slice, then drops the blocks that were already synced.

        The filtering happens here, after the recursion, and not in the record selector: a child block carries its
        own last_edited_time, so an unchanged block still has to be traversed to find its edited descendants.
        """
        filter_synced_blocks = self._has_state_from_previous_sync()
        for block in self._read_block_tree(records_schema, stream_slice):
            if filter_synced_blocks and not self._should_be_synced(block, stream_slice):
                continue
            yield block

    def _has_state_from_previous_sync(self) -> bool:
        # Without a saved cursor value the cursor would compare blocks to the configured start date. Blocks are
        # deliberately not filtered by start date: a page edited after the start date is synced with all of its
        # blocks, however old they are.
        return bool(self.cursor and self.cursor.state.get("state"))

    def _should_be_synced(self, block: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        # Child blocks are read with a slice the cursor does not know about, so they are checked against the slice
        # of the page they belong to.
        return self.cursor.should_be_synced(Record(data=block.data, associated_slice=stream_slice, stream_name=self.name))

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
