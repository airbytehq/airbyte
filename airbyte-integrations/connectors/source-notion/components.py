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

    The CDK only wires client-side incremental filtering into the record selector of a `SimpleRetriever`, so a custom
    retriever never gets it. The model factory still passes the stream cursor (`cursor`) and the
    `is_client_side_incremental_sync` flag, so the filtering on `last_edited_time` is applied here instead:

    - It only applies once a previous sync has stored a global cursor value. A first sync, a reset or a full refresh
      keeps emitting every block, so `start_date` does not start dropping old blocks of recently edited pages.
    - It runs after the recursion, so a child edited since the last sync is still emitted when its parent is unchanged.
    """

    cursor: Optional[Cursor] = None
    is_client_side_incremental_sync: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        # Snapshot the incoming state before the sync starts moving the cursor.
        self._filter_on_cursor = bool(
            self.is_client_side_incremental_sync and self.cursor and self._has_previous_global_cursor_value(self.cursor.state)
        )

    @staticmethod
    def _has_previous_global_cursor_value(state: Mapping[str, Any]) -> bool:
        # Per-partition state is left unfiltered: the cursor has no partition for the nested block slices built below.
        return bool(state.get("use_global_cursor") and state.get("state"))

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

    def _should_be_synced(self, stream_data: StreamData) -> bool:
        if not (self._filter_on_cursor and isinstance(stream_data, Record)):
            return True
        return self.cursor.should_be_synced(stream_data)
