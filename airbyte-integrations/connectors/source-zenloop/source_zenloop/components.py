#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import SubstreamSlicer
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


@dataclass
class ZenloopSubstreamSlicer(SubstreamSlicer):

    config: Config

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        """

        config_parent_field : parent field name in config

        Use parent id's as stream state value if it specified in config or
        create stream_slices according SubstreamSlicer logic.

        """
        parent_field = self._options.get("config_parent_field")
        custom_stream_state_value = self.config.get(parent_field)

        if not custom_stream_state_value:
            yield from super().stream_slices(sync_mode, stream_state)
        else:
            for parent_stream_config in self.parent_stream_configs:
                stream_state_field = parent_stream_config.stream_slice_field or None
                yield {stream_state_field: custom_stream_state_value, "parent_slice": {}}
