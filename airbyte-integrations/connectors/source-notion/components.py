# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import ClientSideIncrementalRecordFilterDecorator, RecordFilter
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor


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

    cursor: Optional[Cursor] = None
    is_client_side_incremental_sync: bool = False
    _incremental_record_filter: Optional[RecordFilter] = field(init=False, default=None)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0
        if isinstance(self.record_selector.record_filter, ClientSideIncrementalRecordFilterDecorator):
            self._incremental_record_filter = self.record_selector.record_filter
            self.record_selector.record_filter = RecordFilter(
                config=self.config,
                parameters=parameters,
                condition=self._incremental_record_filter.condition,
            )
        elif self.is_client_side_incremental_sync and self.cursor:
            self._incremental_record_filter = ClientSideIncrementalRecordFilterDecorator(
                cursor=self.cursor, config=self.config, parameters=parameters
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

            if self._incremental_record_filter is None or any(
                self._incremental_record_filter.filter_records(
                    records=[stream_data.data], stream_state={}, stream_slice=stream_slice
                )
            ):
                yield stream_data
