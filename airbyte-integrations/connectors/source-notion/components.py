# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30
CURSOR_FIELD = "last_edited_time"
logger = logging.getLogger("airbyte")


@dataclass
class BlocksRetriever(SimpleRetriever):
    """
    Docs: https://developers.notion.com/reference/get-block-children

    According to that fact that block's entity may have children entities that stream also need to retrieve
    BlocksRetriever calls read_records when received record.has_children is True.

    Client-side incremental filtering: the CDK only attaches `ClientSideIncrementalRecordFilterDecorator` to the
    record selector of a `SimpleRetriever`. A `CustomRetriever` gets a record selector without the cursor, so the
    `is_client_side_incremental` flag on the stream had no effect and every block was emitted on every sync. When the
    stream starts with saved state, this retriever drops blocks whose `last_edited_time` is before the lower bound
    of the slice's cursor interval (the saved cursor value). Children are still fetched for every block, because
    editing a nested block does not necessarily move its ancestors' `last_edited_time`. Without saved state (first
    sync, reset, full refresh) every block is emitted, as before.
    """

    # Injected by the declarative component factory, which passes the stream's cursor to the retriever it builds.
    cursor: Optional[Cursor] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        self._filter_by_cursor = self._has_saved_state()

    def _has_saved_state(self) -> bool:
        if self.cursor is None:
            return False
        state = self.cursor.state or {}
        return bool(state.get("state") or state.get("states") or state.get(CURSOR_FIELD))

    @staticmethod
    def _lower_bound(stream_slice: Optional[StreamSlice]) -> Optional[datetime]:
        start_time = stream_slice.cursor_slice.get("start_time") if stream_slice else None
        return ab_datetime_parse(start_time) if start_time else None

    def _should_be_synced(self, record: StreamData, lower_bound: Optional[datetime]) -> bool:
        if not self._filter_by_cursor or lower_bound is None:
            return True
        cursor_value = record.get(CURSOR_FIELD) if isinstance(record, Mapping) else None
        if not cursor_value:
            return True
        return ab_datetime_parse(cursor_value) >= lower_bound

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        # if reached recursive limit, don't read anymore
        if self.current_block_depth > MAX_BLOCK_DEPTH:
            logger.info("Reached max block depth limit. Exiting.")
            return

        lower_bound = self._lower_bound(stream_slice)
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

            if self._should_be_synced(stream_data, lower_bound):
                yield stream_data
