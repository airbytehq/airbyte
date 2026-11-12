#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest

from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.core import Stream


class MockStream(Stream):
    def __init__(self, records):
        self.records = records

    def primary_key(self):
        return

    def read_records(self, sync_mode):
        return self.records


# test cases as a list of tuples (boards_records, organizations_records, expected_board_ids)
test_cases = [
    (
        # test same ids in both boards and organizations
        [{"id": "b11111111111111111111111", "name": "board_1"}, {"id": "b22222222222222222222222", "name": "board_2"}],
        [{"id": "org111111111111111111111", "idBoards": ["b11111111111111111111111", "b22222222222222222222222"]}],
        ["b11111111111111111111111", "b22222222222222222222222"],
    ),
    (
        # test one different id in organizations
        [{"id": "b11111111111111111111111", "name": "board_1"}, {"id": "b22222222222222222222222", "name": "board_2"}],
        [{"id": "org111111111111111111111", "idBoards": ["b11111111111111111111111", "b33333333333333333333333"]}],
        ["b11111111111111111111111", "b22222222222222222222222", "b33333333333333333333333"],
    ),
    (
        # test different ids in multiple boards and organizations
        [{"id": "b11111111111111111111111", "name": "board_1"}, {"id": "b22222222222222222222222", "name": "board_2"}],
        [
            {"id": "org111111111111111111111", "idBoards": ["b11111111111111111111111", "b33333333333333333333333"]},
            {"id": "org222222222222222222222", "idBoards": ["b00000000000000000000000", "b44444444444444444444444"]},
        ],
        [
            "b11111111111111111111111",
            "b22222222222222222222222",
            "b33333333333333333333333",
            "b00000000000000000000000",
            "b44444444444444444444444",
        ],
    ),
    (
        # test empty boards and organizations
        [],
        [],
        [],
    ),
]


def concurrent_stream(records):
    stream = Mock(spec=DefaultStream)
    stream.generate_partitions.return_value = [Mock(read=Mock(return_value=[Mock(data=record)])) for record in records]
    return stream


@pytest.mark.parametrize("stream_factory", [MockStream, concurrent_stream])
@pytest.mark.parametrize("boards_records, organizations_records, expected_board_ids", test_cases)
def test_read_all_boards(components_module, boards_records, organizations_records, expected_board_ids, stream_factory):
    OrderIdsPartitionRouter = components_module.OrderIdsPartitionRouter
    # Set up mock streams with provided records
    partition_router = OrderIdsPartitionRouter(parent_stream_configs=[None], config=None, parameters=None)
    boards_stream = stream_factory(records=boards_records)
    organizations_stream = stream_factory(records=organizations_records)

    # Call the function and check the result
    board_ids = list(partition_router.read_all_boards(boards_stream, organizations_stream))
    assert board_ids == expected_board_ids


def test_read_all_boards_propagates_partition_errors(components_module):
    partition_router = components_module.OrderIdsPartitionRouter(parent_stream_configs=[None], config=None, parameters=None)
    stream = Mock(spec=DefaultStream)
    stream.generate_partitions.return_value = [Mock(read=Mock(side_effect=RuntimeError("Unable to read boards")))]

    with pytest.raises(RuntimeError, match="Unable to read boards"):
        list(partition_router.read_all_boards(stream, concurrent_stream([])))
