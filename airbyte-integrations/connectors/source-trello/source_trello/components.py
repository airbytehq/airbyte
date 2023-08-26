#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


@dataclass
class OrdersIdPartitionRouter(SubstreamPartitionRouter):

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
        board_ids = set() # to track the board ids
        for parent_stream_config in self.parent_stream_configs:
            parent_stream = parent_stream_config.stream
            parent_stream_name = parent_stream.name
            parent_field = parent_stream_config.parent_key.eval(self.config)
            stream_state_field = parent_stream_config.partition_field.eval(self.config)
            for parent_stream_slice in parent_stream.stream_slices(
                sync_mode=SyncMode.full_refresh, cursor_field=None, stream_state=None
            ):
                empty_parent_slice = True
                parent_slice = parent_stream_slice

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
                        parent_field_value = dpath.util.get(parent_record, parent_field)
                    except KeyError:
                        pass
                    else:
                        empty_parent_slice = False
                        # iterate idBoards list for organizations stream
                        if parent_stream_name == 'organizations':
                            stream_state_value_list = parent_field_value
                            for stream_state_value in stream_state_value_list:
                                # skip seen board id
                                if stream_state_value not in board_ids:
                                    board_ids.add(stream_state_value)
                                    yield {stream_state_field: stream_state_value, "parent_slice": parent_slice}
                        else:
                            stream_state_value = parent_field_value
                            # skip seen board id
                            if stream_state_value not in board_ids:
                                board_ids.add(stream_state_value)
                                yield {stream_state_field: stream_state_value, "parent_slice": parent_slice}
                # If the parent slice contains no records,
                if empty_parent_slice:
                    yield from []
