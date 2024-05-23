#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.types import StreamSlice, StreamState


@dataclass
class StreamSlicer(RequestOptionsProvider):
    """
    Slices the stream into a subset of records.
    Slices enable state checkpointing and data retrieval parallelization.

    The stream slicer keeps track of the cursor state as a dict of cursor_field -> cursor_value

    See the stream slicing section of the docs for more information.
    """

    @abstractmethod
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Defines stream slices

        :return: List of stream slices
        """

    def set_parent_state(self, stream_state: StreamState) -> None:
        """
        Set the state of the parent streams.

        Args:
            stream_state: The state of the streams to be set. This method can be overridden by subclasses.
        """
        pass

    def get_parent_state(self) -> Optional[StreamState]:
        """
        Get the state of the parent streams.

        Returns:
            The current state of the parent streams. This method can be overridden by subclasses.
        """
        return None
