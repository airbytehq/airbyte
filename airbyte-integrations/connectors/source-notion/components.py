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

    Blocks are filtered against the incoming stream state here rather than in the record selector, after the
    recursion, so that an edited child is still read and emitted when its parent block was not edited. Recent CDKs
    leave a custom retriever's record selector without the client-side incremental filter; older CDKs put it there,
    where it would drop the unedited parent before its children are read, so it is moved out of the selector.
    """

    cursor: Optional[Cursor] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        self._state_cursor = self._move_client_side_incremental_filter_out_of_record_selector() or self.cursor
        self._filter_on_state = self._state_cursor is not None and _has_prior_state(self._state_cursor.state)

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

            if self._is_new_since_prior_state(stream_data):
                yield stream_data

    def _move_client_side_incremental_filter_out_of_record_selector(self) -> Optional[Cursor]:
        record_filter = getattr(self.record_selector, "record_filter", None)
        if not isinstance(record_filter, ClientSideIncrementalRecordFilterDecorator):
            return None
        self.record_selector.record_filter = (
            RecordFilter(config=record_filter.config, condition=record_filter.condition, parameters={}) if record_filter.condition else None
        )
        return record_filter._cursor

    def _is_new_since_prior_state(self, stream_data: StreamData) -> bool:
        if not self._filter_on_state or not isinstance(stream_data, Record):
            return True
        return self._state_cursor.should_be_synced(stream_data)


def _has_prior_state(state: Mapping[str, Any]) -> bool:
    return bool(state.get("state") or state.get("states"))
