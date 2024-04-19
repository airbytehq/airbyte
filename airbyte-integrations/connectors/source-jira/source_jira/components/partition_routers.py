#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


@dataclass
class SubstreamPartitionRouterWithContext(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key.eval(self.config)  # type: ignore # parent_key is always casted to an interpolated string
                partition_field = parent_stream_config.partition_field.eval(self.config)  # type: ignore # partition_field is always casted to an interpolated string
                for parent_stream_slice in parent_stream.stream_slices(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_state=None
                ):
                    empty_parent_slice = True
                    parent_partition = parent_stream_slice.partition if parent_stream_slice else {}

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        # Skip non-records (eg AirbyteLogMessage)
                        if isinstance(parent_record, AirbyteMessage):
                            if parent_record.type == Type.RECORD:
                                parent_record = parent_record.record.data
                            else:
                                continue
                        elif isinstance(parent_record, Record):
                            parent_record = parent_record.data
                        try:
                            partition_value = dpath.util.get(parent_record, parent_field)
                        except KeyError:
                            pass
                        else:
                            empty_parent_slice = False
                            stream_slice = StreamSlice(
                                partition={partition_field: partition_value, "parent_slice": parent_partition}, cursor_slice={}
                            )
                            setattr(stream_slice, "parent_record", parent_record)
                            yield stream_slice
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield from []


class SprintIssuesSubstreamPartitionRouter(SubstreamPartitionRouter):
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        fields_parent_stream_config, *parent_stream_configs = self.parent_stream_configs
        self.fields_parent_stream_config = fields_parent_stream_config
        self.parent_stream_configs = parent_stream_configs

    def stream_slices(self) -> Iterable[StreamSlice]:
        self.parent_stream_configs, parent_stream_configs = [self.fields_parent_stream_config], self.parent_stream_configs
        fields = [s.partition[self.fields_parent_stream_config.partition_field.eval(self.config)] for s in super().stream_slices()]
        fields += ['key', 'status', 'created', 'updated']
        self.parent_stream_configs = parent_stream_configs
        for stream_slice in super().stream_slices():
            setattr(stream_slice, "parent_stream_fields", fields)
            yield stream_slice
