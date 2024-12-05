#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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
                yield StreamSlice(partition={"id": record["id"]}, cursor_slice={})


@dataclass
class ProjectStreamsPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        parent_stream = self.parent_stream_configs[0].stream
        projects_list = self.config.get("projects_list", [])

        group_project_ids = []
        for stream_slice in parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                group_project_ids.extend([i["path_with_namespace"] for i in record["projects"]])

        if group_project_ids:
            for project_id in group_project_ids:
                if not projects_list or projects_list and project_id in projects_list:
                    yield StreamSlice(partition={"id": project_id.replace("/", "%2F")}, cursor_slice={})
        else:
            for project_id in projects_list:
                yield StreamSlice(partition={"id": project_id.replace("/", "%2F")}, cursor_slice={})
