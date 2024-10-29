#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import logging
from collections import ChainMap
from collections.abc import Callable
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.types import StreamSlice, StreamState


def check_for_substream_in_slicers(slicers: Iterable[PartitionRouter], log_warning: Callable[[str], None]) -> None:
    """
    Recursively checks for the presence of SubstreamPartitionRouter within slicers.
    Logs a warning if a SubstreamPartitionRouter is found within a CartesianProductStreamSlicer.

    Args:
        slicers (Iterable[PartitionRouter]): The list of slicers to check.
        log_warning (Callable): Logging function to record warnings.
    """
    for slicer in slicers:
        if isinstance(slicer, SubstreamPartitionRouter):
            log_warning("Parent state handling is not supported for CartesianProductStreamSlicer.")
            return
        elif isinstance(slicer, CartesianProductStreamSlicer):
            # Recursively check sub-slicers within CartesianProductStreamSlicer
            check_for_substream_in_slicers(slicer.stream_slicers, log_warning)


@dataclass
class CartesianProductStreamSlicer(PartitionRouter):
    """
    Stream slicers that iterates over the cartesian product of input stream slicers
    Given 2 stream slicers with the following slices:
    A: [{"i": 0}, {"i": 1}, {"i": 2}]
    B: [{"s": "hello"}, {"s": "world"}]
    the resulting stream slices are
    [
        {"i": 0, "s": "hello"},
        {"i": 0, "s": "world"},
        {"i": 1, "s": "hello"},
        {"i": 1, "s": "world"},
        {"i": 2, "s": "hello"},
        {"i": 2, "s": "world"},
    ]

    Attributes:
        stream_slicers (List[PartitionRouter]): Underlying stream slicers. The RequestOptions (e.g: Request headers, parameters, etc..) returned by this slicer are the combination of the RequestOptions of its input slicers. If there are conflicts e.g: two slicers define the same header or request param, the conflict is resolved by taking the value from the first slicer, where ordering is determined by the order in which slicers were input to this composite slicer.
    """

    stream_slicers: List[PartitionRouter]
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        check_for_substream_in_slicers(self.stream_slicers, self.logger.warning)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def stream_slices(self) -> Iterable[StreamSlice]:
        sub_slices = (s.stream_slices() for s in self.stream_slicers)
        product = itertools.product(*sub_slices)
        for stream_slice_tuple in product:
            partition = dict(ChainMap(*[s.partition for s in stream_slice_tuple]))  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
            cursor_slices = [s.cursor_slice for s in stream_slice_tuple if s.cursor_slice]
            if len(cursor_slices) > 1:
                raise ValueError(f"There should only be a single cursor slice. Found {cursor_slices}")
            if cursor_slices:
                cursor_slice = cursor_slices[0]
            else:
                cursor_slice = {}
            yield StreamSlice(partition=partition, cursor_slice=cursor_slice)

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Parent stream states are not supported for cartesian product stream slicer
        """
        pass

    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        """
        Parent stream states are not supported for cartesian product stream slicer
        """
        pass

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger("airbyte.CartesianProductStreamSlicer")
