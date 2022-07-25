#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class StreamSlicer(ABC):
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
    def get_stream_state(self) -> Optional[StreamState]:
        """Returns the current stream state"""

    @abstractmethod
    def request_params(self) -> Mapping[str, Any]:
        """Specifies the query parameters that should be set on an outgoing HTTP request given the inputs."""

    @abstractmethod
    def request_headers(self) -> Mapping[str, Any]:
        """Specifies the request headers that should be set on an outgoing HTTP request given the inputs."""

    @abstractmethod
    def request_body_data(self) -> Mapping[str, Any]:
        """Specifies how to populate the body of the request with a non-JSON payload."""

    @abstractmethod
    def request_body_json(self) -> Mapping[str, Any]:
        """Specifies how to populate the body of the request with a JSON payload."""
