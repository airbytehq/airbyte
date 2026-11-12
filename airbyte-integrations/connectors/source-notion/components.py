# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from copy import copy
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

    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        self._incremental_record_filter = None
        if isinstance(self.record_selector.record_filter, ClientSideIncrementalRecordFilterDecorator):
            self._incremental_record_filter = self.record_selector.record_filter
            self.record_selector = copy(self.record_selector)
            self.record_selector.record_filter = (
                RecordFilter(
                    config=self._incremental_record_filter.config,
                    condition=self._incremental_record_filter.condition,
                    parameters=self.record_selector._parameters,
                )
                if self._incremental_record_filter.condition
                else None
            )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
        parent_stream_slice: Optional[StreamSlice] = None,
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
                yield from self.read_records(records_schema, child_stream_slice, parent_stream_slice=parent_stream_slice or stream_slice)
                self.current_block_depth -= 1

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            if self._incremental_record_filter is None or any(
                self._incremental_record_filter.filter_records(
                    [stream_data.data], stream_state=self.state, stream_slice=parent_stream_slice or stream_slice
                )
            ):
                yield (
                    Record(
                        data=stream_data.data,
                        stream_name=stream_data.stream_name,
                        associated_slice=parent_stream_slice,
                        file_reference=stream_data.file_reference,
                    )
                    if parent_stream_slice
                    else stream_data
                )
