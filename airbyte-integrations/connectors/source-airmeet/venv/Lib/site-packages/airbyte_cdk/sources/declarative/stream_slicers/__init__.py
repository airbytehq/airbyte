#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer_test_read_decorator import (
    StreamSlicerTestReadDecorator,
)

__all__ = ["StreamSlicer", "StreamSlicerTestReadDecorator"]
