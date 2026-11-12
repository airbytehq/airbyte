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

    Incremental filtering on `last_edited_time` is applied here, after the children of a block were read, and not in the
    record selector: a block's `last_edited_time` does not tell whether its children changed, so every block has to be
    traversed even when the block itself is not emitted.
    """

    # Both are passed by the CDK's component factory, which fills the fields a custom component declares.
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

            if self._should_be_emitted(stream_data):
                yield stream_data

    def _should_be_emitted(self, record: Record) -> bool:
        """
        Once a previous sync has completed, only blocks edited since then are emitted. Until then every block is
        emitted, including blocks last edited before the configured start date, as a recently edited page is mostly
        made of blocks that have not been edited for a long time.
        """
        if not self.is_client_side_incremental_sync or self.cursor is None:
            return True
        # the stream uses a global substream cursor, whose value is only set once a sync went through every page
        if not self.cursor.state.get("state"):
            return True
        return self.cursor.should_be_synced(record)
