#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class Retriever(JsonSchemaMixin):
    """
    Responsible for fetching a stream's records from an HTTP API source.
    """

    @abstractmethod
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
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
    def stream_slices(self, *, sync_mode: SyncMode, stream_state: Optional[StreamState] = None) -> Iterable[Optional[StreamSlice]]:
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
    def state(self, value: StreamState):
        """State setter, accept state serialized by state getter."""
