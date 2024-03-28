# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Union

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.models import ParentStreamConfig
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class ThreadsPartitionRouter(SubstreamPartitionRouter):
    """Overwrite SubstreamPartitionRouter to be able to pass more than one value
    from parent stream to stream_slices
    """

    def _get_threads_request_params(
        self, channel: str, stream_slice: Optional[StreamSlice] = None, stream_state: Optional[StreamState] = None
    ) -> Mapping[str, Any]:
        """
        Validates that the request params are >= than current state values for incremental syncs.
        Threads request should be performed only for float_ts from slice >= current float ts from state.
        """
        if stream_state:
            for state in stream_state["states"]:
                if state["partition"]["channel"] == channel:
                    float_ts = state["cursor"]["float_ts"]
                    if float(stream_slice.partition["float_ts"]) >= float(float_ts):
                        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)
                    else:
                        return {}

        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        channel = stream_slice.partition.get("channel") if stream_slice else None
        if channel:
            return self._get_threads_request_params(channel, stream_slice, stream_state)

        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

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
