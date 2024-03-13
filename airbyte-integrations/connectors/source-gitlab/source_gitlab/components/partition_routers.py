#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class GroupStreamsPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        parent_streams = {stream.stream.name: stream.stream for stream in self.parent_stream_configs}
        groups_list = self.config.get("groups_list")
        selected_parent = parent_streams["include_descendant_groups"] if groups_list else parent_streams["groups_list"]

        for stream_slice in selected_parent.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in selected_parent.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                yield {"id": record["id"]}
