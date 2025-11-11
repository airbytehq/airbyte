#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC

from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import (
    RequestOptionsProvider,
)
from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import (
    StreamSlicer as ConcurrentStreamSlicer,
)


class StreamSlicer(ConcurrentStreamSlicer, RequestOptionsProvider, ABC):
    """
    Slices the stream into a subset of records.
    Slices enable state checkpointing and data retrieval parallelization.

    The stream slicer keeps track of the cursor state as a dict of cursor_field -> cursor_value

    See the stream slicing section of the docs for more information.
    """

    pass
