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

    Client-side incremental filtering: when the stream is configured with `is_client_side_incremental`, the CDK passes
    the stream `cursor` and `is_client_side_incremental_sync` to custom retrievers but does not wrap the record
    selector of a custom retriever with the cursor filter. The filter is therefore applied here, when records are
    emitted. Children are still traversed for blocks that are filtered out, because editing a nested block does not
    update the `last_edited_time` of its ancestors.
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

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            if self._should_be_synced(stream_data, stream_slice):
                yield stream_data

    def _should_be_synced(self, stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        if not (self.is_client_side_incremental_sync and self.cursor):
            return True
        record = (
            stream_data
            if isinstance(stream_data, Record) and stream_data.associated_slice
            else Record(data=stream_data.data, associated_slice=stream_slice, stream_name=self.name)
        )
        return self.cursor.should_be_synced(record)
