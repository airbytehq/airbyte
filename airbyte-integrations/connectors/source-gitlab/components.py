#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from typing import Any, Iterable, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.declarative.validators import ValidationStrategy
from airbyte_cdk.utils import is_cloud_environment


@dataclass
class ValidateApiUrl(ValidationStrategy):
    def validate(self, value: Any) -> None:
        url: str = value
        is_valid, scheme, _ = self._parse_url(url=url)
        if not is_valid:
            raise ValueError("Invalid API resource locator.")
        if scheme == "http" and is_cloud_environment():
            raise ValueError("Http scheme is not allowed in this environment. Please use `https` instead.")

    @staticmethod
    def _parse_url(url: str) -> Tuple[bool, str, str]:
        if not "." in url:
            return False, "", ""
        parts = url.split("://")
        if len(parts) > 1:
            scheme, url = parts
        else:
            scheme = "https"
        if scheme not in ("http", "https"):
            return False, "", ""
        parts = url.split("/", 1)
        if len(parts) > 1:
            return False, "", ""
        host, *_ = parts
        return True, scheme, host


@dataclass
class GroupStreamsPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        parent_streams = {stream.stream.name: stream.stream for stream in self.parent_stream_configs}
        groups_list = self.config.get("groups_list")
        selected_parent = parent_streams["include_descendant_groups"] if groups_list else parent_streams["groups_list"]

        for partition in selected_parent.generate_partitions():
            for record in partition.read():
                yield StreamSlice(partition={"id": record["id"]}, cursor_slice={})


@dataclass
class ProjectStreamsPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        parent_stream = self.parent_stream_configs[0].stream
        projects_list = self.config.get("projects_list", [])

        group_project_ids = []
        for partition in parent_stream.generate_partitions():
            for record in partition.read():
                group_project_ids.extend([i["path_with_namespace"] for i in record["projects"]])

        if group_project_ids:
            for project_id in group_project_ids:
                if not projects_list or projects_list and project_id in projects_list:
                    yield StreamSlice(partition={"id": project_id.replace("/", "%2F")}, cursor_slice={})
        else:
            for project_id in projects_list:
                yield StreamSlice(partition={"id": project_id.replace("/", "%2F")}, cursor_slice={})
