#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import itertools
from collections import ChainMap
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


class CartesianProductStreamSlicer(StreamSlicer):
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
    """

    def path(self) -> Optional[str]:
        pass

    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]]):
        pass

    def request_params(self) -> Mapping[str, Any]:
        pass

    def request_headers(self) -> Mapping[str, Any]:
        pass

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        pass

    def request_body_json(self) -> Optional[Mapping]:
        pass

    def set_state(self, stream_state: Mapping[str, Any]):
        pass

    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        pass

    def __init__(self, stream_slicers: List[StreamSlicer]):
        self._stream_slicers = stream_slicers

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        sub_slices = (s.stream_slices(sync_mode, stream_state) for s in self._stream_slicers)
        return (ChainMap(*a) for a in itertools.product(*sub_slices))
