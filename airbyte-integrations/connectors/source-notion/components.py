# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
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

    The CDK only wires the client-side incremental filter into the record selector of a `SimpleRetriever` it builds
    itself. For a `CustomRetriever` it passes `cursor` and `is_client_side_incremental_sync` as keyword arguments
    instead, so this retriever declares both and filters on the cursor here. The filter runs after the recursion on
    purpose: a block that was not edited is still walked, so an edited child below it is not missed.
    """

    cursor: Optional[Any] = None
    is_client_side_incremental_sync: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0

    def read_records(
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
                yield from self.read_records(records_schema, child_stream_slice)
                self.current_block_depth -= 1

            if not self._should_be_synced(stream_data, stream_slice):
                continue

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            yield stream_data

    def _should_be_synced(self, stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        """Drop the blocks last edited before the stream state (or the start date) when the stream is client-side incremental."""
        if not self.is_client_side_incremental_sync or self.cursor is None:
            return True
        if isinstance(stream_data, Record):
            record = stream_data
        else:
            record = Record(data=stream_data, associated_slice=stream_slice, stream_name=self.name)
        return bool(self.cursor.should_be_synced(record))
