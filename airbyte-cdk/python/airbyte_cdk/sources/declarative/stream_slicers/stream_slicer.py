#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class StreamSlicer(RequestOptionsProvider, JsonSchemaMixin):
    """
    Slices the stream into a subset of records.
    Slices enable state checkpointing and data retrieval parallelization.

    The stream slicer keeps track of the cursor state as a dict of cursor_field -> cursor_value

    See the stream slicing section of the docs for more information.
    """

    @abstractmethod
    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        """
        Defines stream slices

        :param sync_mode: The sync mode used the read data
        :param stream_state: The current stream state
        :return: List of stream slices
        """

    @abstractmethod
    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        """
        State setter, accept state serialized by state getter.

        :param stream_slice: Current stream_slice
        :param last_record: Last record read from the source
        """

    @abstractmethod
    def get_stream_state(self) -> StreamState:
        """Returns the current stream state"""
