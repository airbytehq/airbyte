# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import ClientSideIncrementalRecordFilterDecorator, RecordFilter
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

    Client-side incremental filtering on `last_edited_time` is applied here rather than in the record selector:
    - the record selector of a CustomRetriever does not always receive the stream cursor from the CDK, in which case
      no incremental filtering would happen and every block would be emitted on every sync;
    - a block whose own `last_edited_time` is older than the state can still have children that were edited
      recently, so the recursion must see every block before the cursor decides which ones are emitted.
    """

    cursor: Optional[Any] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        # On CDK versions where the record selector does not receive the cursor, it is passed to the retriever as `cursor`
        self._client_side_cursor = self.cursor
        record_filter = self.record_selector.record_filter
        if isinstance(record_filter, ClientSideIncrementalRecordFilterDecorator):
            # keep the record_filter condition in the selector but move the cursor filtering to read_records
            self._client_side_cursor = record_filter._cursor
            self.record_selector.record_filter = RecordFilter(config=self.config, condition=record_filter.condition, parameters=parameters)

    def _should_be_synced(self, stream_data: StreamData) -> bool:
        cursor = self._client_side_cursor
        if cursor is None or not hasattr(cursor, "should_be_synced") or not isinstance(stream_data, Record):
            return True
        return cursor.should_be_synced(stream_data)

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

            if self._should_be_synced(stream_data):
                yield stream_data
