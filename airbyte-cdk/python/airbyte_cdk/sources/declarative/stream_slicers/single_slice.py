#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


class SingleSlice(StreamSlicer):
    def __init__(self, **kwargs):
        pass

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return [dict()]
