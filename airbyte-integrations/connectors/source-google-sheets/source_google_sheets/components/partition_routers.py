#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.types import StreamSlice
from source_google_sheets.batch_size_manager import BatchSizeManager


logger = logging.getLogger("airbyte")


class RangePartitionRouter(SinglePartitionRouter):
    """
    Create ranges to request rows data to google sheets api.
    """

    parameters: Mapping[str, Any]

    def __init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__(parameters)
        self.parameters = parameters
        self.sheet_row_count = parameters.get("row_count", 0)
        self.batch_size_manager = BatchSizeManager(parameters.get("batch_size", 200))

    def stream_slices(self) -> Iterable[StreamSlice]:
        start_range = 2
        while start_range <= self.sheet_row_count:
            end_range = start_range + self.batch_size_manager.get_batch_size()
            logger.info(f"Fetching start_range: {start_range}, end_range: {end_range}")
            yield StreamSlice(partition={"start_range": start_range, "end_range": end_range}, cursor_slice={})
            start_range = end_range + 1
