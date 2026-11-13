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

    The CDK does not apply the client-side incremental filter to the record selector of a custom retriever, and it
    could not be applied there anyway: a block edited before the stream state can still hold children edited after it,
    so every block has to be traversed first and filtered only when it is emitted.
    """

    # Stream cursor, passed by the CDK when it builds the retriever. None when the stream has no incremental sync.
    cursor: Optional[Cursor] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        # Only a sync that resumes from a saved state drops blocks. A first sync (or a full refresh) keeps emitting
        # every block of the pages it reads, including the ones last edited before `start_date`, as it always did.
        incoming_state = self.cursor.state if self.cursor else {}
        self._filter_already_synced_blocks = bool(incoming_state.get("state") or incoming_state.get("states"))

    def _should_be_synced(self, block: Record, page_slice: Optional[StreamSlice]) -> bool:
        if not self._filter_already_synced_blocks:
            return True
        # The cursor is asked about the page slice, not the child block slice the record was read with: the stream
        # state only knows the partitions made of pages.
        return self.cursor.should_be_synced(Record(data=block.data, associated_slice=page_slice, stream_name=self.name))

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        yield from self._read_blocks(records_schema, stream_slice, page_slice=stream_slice)

    def _read_blocks(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice],
        page_slice: Optional[StreamSlice],
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
                yield from self._read_blocks(records_schema, child_stream_slice, page_slice)
                self.current_block_depth -= 1

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            # filtered after the children are read: an unchanged block can hold changed children
            if self._should_be_synced(stream_data, page_slice):
                yield stream_data
