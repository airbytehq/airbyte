# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Union

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.models import ParentStreamConfig
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


@dataclass
class ThreadsPartitionRouter(SubstreamPartitionRouter):
    """Overwrite SubstreamPartitionRouter to be able to pass more than one value
    from parent stream to stream_slices
    """

    def _get_parent_field(self, parent_stream_config: ParentStreamConfig) -> str:
        parent_field = parent_stream_config.parent_key.eval(self.config)  # type: ignore # parent_key is always casted to an interpolated string
        return parent_field

    def _get_partition_field(self, parent_stream_config: ParentStreamConfig) -> str:
        partition_field = parent_stream_config.partition_field.eval(self.config)  # type: ignore # partition_field is always casted to an interpolated string
        return partition_field

    @staticmethod
    def _parse_read_output(parent_record: Union[AirbyteMessage, Record]) -> Union[dict[str, Any], Mapping[str, Any], None]:
        # Skip non-records (eg AirbyteLogMessage)
        if isinstance(parent_record, AirbyteMessage):
            if parent_record.type == Type.RECORD:
                return parent_record.record.data
            else:
                return
        if isinstance(parent_record, Record):
            return parent_record.data

    @staticmethod
    def _get_partition_value(parent_record: Union[dict[str, Any], Mapping[str, Any]], parent_field: str) -> str:
        partition_value = None
        try:
            partition_value = dpath.util.get(parent_record, parent_field)
        except KeyError:
            pass

        return partition_value

    @staticmethod
    def _create_stream_slice(partition_field: str, partition_value: str, parent_partition: dict[str, Any]) -> StreamSlice:
        return StreamSlice(partition={partition_field: partition_value, "channel": parent_partition["channel"]}, cursor_slice={})

    def stream_slices(self) -> Iterable[StreamSlice]:
        if not self.parent_stream_configs:
            yield StreamSlice(partition={}, cursor_slice={})
        else:
            for parent_stream_config in self.parent_stream_configs:

                parent_stream = parent_stream_config.stream
                parent_field = self._get_parent_field(parent_stream_config)
                partition_field = self._get_partition_field(parent_stream_config)

                for parent_stream_slice in parent_stream.stream_slices(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_state=None
                ):

                    empty_parent_slice = True
                    parent_partition = parent_stream_slice.partition if parent_stream_slice else {}

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        parent_record = self._parse_read_output(parent_record)
                        if not parent_record:
                            continue

                        partition_value = self._get_partition_value(parent_record, parent_field)
                        empty_parent_slice = False if partition_value else True

                        if not empty_parent_slice:
                            yield self._create_stream_slice(partition_field, partition_value, parent_partition)

                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield StreamSlice(partition={}, cursor_slice={})
