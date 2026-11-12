# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30
# must match the default `start_date` of `client_side_incremental_sync` in manifest.yaml
DEFAULT_START_DATE_DAYS_AGO = 730
logger = logging.getLogger("airbyte")


@dataclass
class BlocksRetriever(SimpleRetriever):
    """
    Docs: https://developers.notion.com/reference/get-block-children

    According to that fact that block's entity may have children entities that stream also need to retrieve
    BlocksRetriever calls read_records when received record.has_children is True.

    Incremental filtering: the CDK only attaches the client-side incremental record filter to the record selector of a
    `SimpleRetriever` built by the factory, not to one nested inside a `CustomRetriever`, so every block would be
    emitted on every incremental sync. This retriever therefore drops blocks whose `last_edited_time` is older than the
    slice's `start_time` when that start comes from the stream state, i.e. when it is later than the configured (or
    default) start date. A slice that starts at the start date (first sync, full refresh) is not filtered, so the set of
    blocks those reads emit is unchanged. The check is done when a block is yielded, after its children have been read,
    so an edited child of an unchanged parent block is still emitted.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        # Evaluated after the stream's cursor is created, so the default is never earlier than the cursor's own default.
        configured_start_date = self.config.get("start_date")
        self._start_date: datetime = (
            ab_datetime_parse(configured_start_date)
            if configured_start_date
            else ab_datetime_now() - timedelta(days=DEFAULT_START_DATE_DAYS_AGO)
        )

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

            if self._is_edited_since_state(stream_data, stream_slice):
                yield stream_data

    def _is_edited_since_state(self, stream_data: StreamData, stream_slice: Optional[StreamSlice]) -> bool:
        start_time = stream_slice.cursor_slice.get("start_time") if stream_slice else None
        last_edited_time = stream_data.get("last_edited_time")
        if not start_time or not last_edited_time:
            return True
        slice_start = ab_datetime_parse(start_time)
        if slice_start <= self._start_date:
            return True
        return ab_datetime_parse(last_edited_time) >= slice_start
