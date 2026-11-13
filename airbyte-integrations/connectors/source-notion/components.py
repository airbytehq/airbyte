# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30
logger = logging.getLogger("airbyte")


@dataclass
class BlocksRetriever(SimpleRetriever):
    """
    Docs: https://developers.notion.com/reference/get-block-children

    According to that fact that block's entity may have children entities that stream also need to retrieve
    BlocksRetriever calls read_records when received record.has_children is True.

    Incremental filtering happens here, after the children are fetched, instead of in the record selector:
    a block's `last_edited_time` is not guaranteed to change when one of its children is edited, so dropping an old
    parent block before recursing would also drop its recently edited children. The manifest therefore
    leaves `is_client_side_incremental` off for this stream and the retriever only emits blocks edited
    at or after the slice's `start_time`.
    """

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

            if self._is_edited_since_slice_start(stream_data, stream_slice):
                yield stream_data

    @staticmethod
    def _is_edited_since_slice_start(stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        start_time = stream_slice.cursor_slice.get("start_time") if stream_slice and stream_slice.cursor_slice else None
        last_edited_time = stream_data.get("last_edited_time") if hasattr(stream_data, "get") else None
        if not start_time or not last_edited_time:
            return True
        return ab_datetime_parse(last_edited_time) >= ab_datetime_parse(start_time)
