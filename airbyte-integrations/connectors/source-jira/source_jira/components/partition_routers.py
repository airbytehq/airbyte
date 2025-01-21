#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


class SprintIssuesSubstreamPartitionRouter(SubstreamPartitionRouter):
    """
    We often require certain data to be fully retrieved from the parent stream before we begin requesting data from the child stream.
    In this custom component, we execute stream slices twice: first, we retrieve all the parent_stream_fields,
    and then we call stream slices again, this time with the previously fetched fields.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        fields_parent_stream_config, *parent_stream_configs = self.parent_stream_configs
        self.fields_parent_stream_config = fields_parent_stream_config
        self.parent_stream_configs = parent_stream_configs

    def stream_slices(self) -> Iterable[StreamSlice]:
        self.parent_stream_configs, parent_stream_configs = [self.fields_parent_stream_config], self.parent_stream_configs
        fields = [s.partition[self.fields_parent_stream_config.partition_field.eval(self.config)] for s in super().stream_slices()]
        fields += ["key", "status", "created", "updated"]
        self.parent_stream_configs = parent_stream_configs
        for stream_slice in super().stream_slices():
            setattr(stream_slice, "parent_stream_fields", fields)
            yield stream_slice


class SubstreamOrSinglePartitionRouter(SubstreamPartitionRouter):
    """
    Depending on the configuration option, we may or may not need to iterate over the parent stream.
    By default, if no projects are set, the child stream should produce records as a normal stream without the parent stream.

    If we do not specify a project in a child stream, it means we are requesting information for all of them,
    so there is no need to slice by all the projects and request data as many times as we have projects one by one.
    That's why an empty slice is returned.

    If projects are defined in the configuration,
    we need to iterate over the given projects and provide a child stream with a slice per project so that it can make a query per project.

    Therefore, if the option is not set, it does not necessarily mean there is no data.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        if self.config.get("projects"):
            yield from super().stream_slices()
        else:
            yield from [StreamSlice(partition={}, cursor_slice={})]
