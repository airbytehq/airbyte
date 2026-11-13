# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import ClientSideIncrementalRecordFilterDecorator, RecordFilter
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice
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

    The client-side incremental filter (`last_edited_time` against the stream's cursor) is applied here, after the
    recursion, and not in the record selector: a block that has not changed still has to be walked, because Notion
    does not reliably bump a parent block's `last_edited_time` when one of its descendants is edited.
    """

    # The stream's cursor. Recent CDK versions pass it to the retriever as `cursor`; older ones only pass it as the
    # `stream_slicer`, see `_client_side_incremental_cursor`.
    cursor: Optional[Cursor] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0

        # Depending on the CDK version, the factory may wrap the selector's record filter with the client-side
        # incremental filter. That would drop unchanged parent blocks before their children are fetched, so keep only
        # the manifest's own `record_filter` condition in the selector and do the cursor filtering in `read_records`.
        record_filter = getattr(self.record_selector, "record_filter", None)
        if isinstance(record_filter, ClientSideIncrementalRecordFilterDecorator):
            self.record_selector.record_filter = (
                RecordFilter(config=self.config, condition=record_filter.condition, parameters=parameters)
                if record_filter.condition
                else None
            )

    def _client_side_incremental_cursor(self) -> Optional[Cursor]:
        for candidate in (self.cursor, self.stream_slicer):
            if isinstance(candidate, Cursor):
                return candidate
        return None

    def _should_be_synced(self, record: StreamData) -> bool:
        cursor = self._client_side_incremental_cursor()
        return cursor is None or cursor.should_be_synced(record)

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
