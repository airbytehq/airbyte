#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.core import Stream


@dataclass
class OrderIdsPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        stream_map = {stream_config.stream.name: stream_config.stream for stream_config in self.parent_stream_configs}

        board_ids = set(self.config.get("board_ids", []))
        if not board_ids:
            board_ids = self.read_all_boards(stream_boards=stream_map["boards"], stream_organizations=stream_map["organizations"])

        for board_id in board_ids:
            yield StreamSlice(partition={"id": board_id}, cursor_slice={})

    def read_all_boards(self, stream_boards: Stream, stream_organizations: Stream):
        """
        Method to get id of each board in the boards stream,
        get ids of boards associated with each organization in the organizations stream
        and yield each unique board id
        """
        board_ids = set()

        for record in stream_boards.read_records(sync_mode=SyncMode.full_refresh):
            if record["id"] not in board_ids:
                board_ids.add(record["id"])
                yield record["id"]

        for record in stream_organizations.read_records(sync_mode=SyncMode.full_refresh):
            for board_id in record["idBoards"]:
                if board_id not in board_ids:
                    board_ids.add(board_id)
                    yield board_id
