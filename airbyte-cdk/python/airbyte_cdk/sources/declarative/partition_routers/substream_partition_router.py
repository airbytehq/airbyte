#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Union

import dpath
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState

if TYPE_CHECKING:
    from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream


@dataclass
class ParentStreamConfig:
    """
    Describes how to create a stream slice from a parent stream

    stream: The stream to read records from
    parent_key: The key of the parent stream's records that will be the stream slice key
    partition_field: The partition key
    request_option: How to inject the slice value on an outgoing HTTP request
    incremental_dependency (bool): Indicates if the parent stream should be read incrementally.
    """

    stream: "DeclarativeStream"  # Parent streams must be DeclarativeStream because we can't know which part of the stream slice is a partition for regular Stream
    parent_key: Union[InterpolatedString, str]
    partition_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    request_option: Optional[RequestOption] = None
    incremental_dependency: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.parent_key = InterpolatedString.create(self.parent_key, parameters=parameters)
        self.partition_field = InterpolatedString.create(self.partition_field, parameters=parameters)


@dataclass
class SubstreamPartitionRouter(PartitionRouter):
    """
    Partition router that iterates over the parent's stream records and emits slices
    Will populate the state with `partition_field` and `parent_slice` so they can be accessed by other components

    Attributes:
        parent_stream_configs (List[ParentStreamConfig]): parent streams to iterate over and their config
    """

    parent_stream_configs: List[ParentStreamConfig]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if not self.parent_stream_configs:
            raise ValueError("SubstreamPartitionRouter needs at least 1 parent stream")
        self._parameters = parameters
        self._parent_state: Dict[str, Any] = {}

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: Optional[StreamSlice]) -> Mapping[str, Any]:
        params = {}
        if stream_slice:
            for parent_config in self.parent_stream_configs:
                if parent_config.request_option and parent_config.request_option.inject_into == option_type:
                    key = parent_config.partition_field.eval(self.config)  # type: ignore # partition_field is always casted to an interpolated string
                    value = stream_slice.get(key)
                    if value:
                        params.update({parent_config.request_option.field_name.eval(config=self.config): value})  # type: ignore # field_name is always casted to an interpolated string
        return params

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Iterate over each parent stream's record and create a StreamSlice for each record.

        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each record.
        yield a stream slice for each such records.

        If a parent slice contains no record, emit a slice with parent_record=None.

        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name
        """
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key.eval(self.config)  # type: ignore # parent_key is always casted to an interpolated string
                partition_field = parent_stream_config.partition_field.eval(self.config)  # type: ignore # partition_field is always casted to an interpolated string
                incremental_dependency = parent_stream_config.incremental_dependency
                for parent_stream_slice in parent_stream.stream_slices(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_state=None
                ):
                    parent_partition = parent_stream_slice.partition if parent_stream_slice else {}

                    # we need to read all records for slice to update the parent stream cursor
                    stream_slices_for_parent = []

                    # only stream_slice param is used in the declarative stream, stream state is set in PerPartitionCursor set_initial_state
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
                            partition_value = dpath.get(parent_record, parent_field)
                        except KeyError:
                            pass
                        else:
                            stream_slices_for_parent.append(
                                StreamSlice(partition={partition_field: partition_value, "parent_slice": parent_partition}, cursor_slice={})
                            )

                    # update the parent state, as parent stream read all record for current slice and state is already updated
                    if incremental_dependency:
                        self._parent_state[parent_stream.name] = parent_stream.state

                    yield from stream_slices_for_parent

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the state of the parent streams.

        Args:
            stream_state (StreamState): The state of the streams to be set. If `parent_state` exists in the
            stream_state, it will update the state of each parent stream with the corresponding state from the stream_state.

        Example of state format:
        {
            "parent_state": {
                "parent_stream_name1": {
                    "last_updated": "2023-05-27T00:00:00Z"
                },
                "parent_stream_name2": {
                    "last_updated": "2023-05-27T00:00:00Z"
                }
            }
        }
        """
        if not stream_state:
            return

        parent_state = stream_state.get("parent_state")
        if not parent_state:
            return

        for parent_config in self.parent_stream_configs:
            if parent_config.incremental_dependency:
                parent_config.stream.state = parent_state.get(parent_config.stream.name, {})

    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        """
        Get the state of the parent streams.

        Returns:
            StreamState: The current state of the parent streams.

        Example of state format:
        {
            "parent_stream_name1": {
                "last_updated": "2023-05-27T00:00:00Z"
            },
            "parent_stream_name2": {
                "last_updated": "2023-05-27T00:00:00Z"
            }
        }
        """
        return self._parent_state
