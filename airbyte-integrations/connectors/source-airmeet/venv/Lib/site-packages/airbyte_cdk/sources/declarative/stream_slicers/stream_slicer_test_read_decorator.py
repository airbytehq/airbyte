#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from itertools import islice
from typing import Any, Iterable

from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import StreamSlicer
from airbyte_cdk.sources.types import StreamSlice


@dataclass
class StreamSlicerTestReadDecorator(StreamSlicer):
    """
    In some cases, we want to limit the number of requests that are made to the backend source. This class allows for limiting the number of
    slices that are queried throughout a read command.
    """

    wrapped_slicer: StreamSlicer
    maximum_number_of_slices: int = 5

    def stream_slices(self) -> Iterable[StreamSlice]:
        return islice(self.wrapped_slicer.stream_slices(), self.maximum_number_of_slices)

    def __getattr__(self, name: str) -> Any:
        # Delegate everything else to the wrapped object
        return getattr(self.wrapped_slicer, name)
