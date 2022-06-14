#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import itertools
from collections import ChainMap
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


class CartesianProductStreamSlicer(StreamSlicer):
    def __init__(self, stream_slicers: List[StreamSlicer]):
        self._stream_slicers = stream_slicers

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return (ChainMap(*a) for a in itertools.product(*(s.stream_slices(sync_mode, stream_state) for s in self._stream_slicers)))
