#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState


class RangePartitionRouter(SinglePartitionRouter):
    def __init__(self, row_count: int = 0, batch_size: int = 200, **kwargs):
        super().__init__(**kwargs)
        self.row_count = row_count
        self.batch_size = batch_size

    def stream_slices(self) -> Iterable[StreamSlice]:
        start_range = 2
        while start_range <= self.row_count:
            end_range = start_range + self.batch_size
            yield StreamSlice(partition={"start_range": start_range, "end_range": end_range}, cursor_slice={})
            start_range += self.batch_size + 1


class RangeRetriever(SimpleRetriever):
    parameters: Mapping[str, Any]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        parameters = kwargs.get("parameters")
        self.stream_slicer: StreamSlicer = RangePartitionRouter(
            parameters={}, row_count=parameters.get("row_count", 0), batch_size=self.config.get("batch_size", 200)
        )

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:  # type: ignore
        return self.stream_slicer.stream_slices()
