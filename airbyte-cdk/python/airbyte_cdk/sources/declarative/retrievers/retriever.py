#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData


@dataclass
class Retriever:
    """
    Responsible for fetching a stream's records from an HTTP API source.
    """

    @abstractmethod
    def read_records(
        self,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        """
        Fetch a stream's records from an HTTP API source

        :param sync_mode: Unused but currently necessary for integrating with HttpStream
        :param cursor_field: Unused but currently necessary for integrating with HttpStream
        :param stream_slice: The stream slice to read data for
        :param stream_state: The initial stream state
        :return: The records read from the API source
        """

    @abstractmethod
    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        """Returns the stream slices"""

    @property
    @abstractmethod
    def state(self) -> StreamState:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a cursor_value:
            {
                self.cursor_field: "cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

    @state.setter
    @abstractmethod
    def state(self, value: StreamState) -> None:
        """State setter, accept state serialized by state getter."""
