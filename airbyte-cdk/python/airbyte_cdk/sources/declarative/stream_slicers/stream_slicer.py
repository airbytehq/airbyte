#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional

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

        This method should only be defined if the slicer is based on some parent stream and needs to read this stream
        incrementally using the state.

        Args:
            stream_state (StreamState): The state of the streams to be set. The expected format is a dictionary that includes
                                        'parent_state' which is a dictionary of parent state names to their corresponding state.
                                        Example:
                                        {
                                            "parent_state": {
                                                "parent_stream_name_1": { ... },
                                                "parent_stream_name_2": { ... },
                                                ...
                                            }
                                        }
        """
        pass

    def get_parent_state(self) -> Optional[Mapping[str, StreamState]]:
        """
        Get the state of the parent streams.

        This method should only be defined if the slicer is based on some parent stream and needs to read this stream
        incrementally using the state.

        Returns:
            Optional[Mapping[str, StreamState]]: The current state of the parent streams in a dictionary format.
                                                 The returned format will be:
                                                 {
                                                     "parent_stream_name1": {
                                                         "last_updated": "2023-05-27T00:00:00Z"
                                                     },
                                                     "parent_stream_name2": {
                                                         "last_updated": "2023-05-27T00:00:00Z"
                                                     }
                                                 }
        """
        return None
