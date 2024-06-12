# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC

from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.checkpoint.cursor import Cursor


class DeclarativeCursor(Cursor, StreamSlicer, ABC):
    """
    DeclarativeCursors are components that allow for checkpointing syncs. In addition to managing the fetching and updating of
    state, declarative cursors also manage stream slicing and injecting slice values into outbound requests.
    """
