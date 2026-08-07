#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest

from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.core import Stream


class MockStream(Stream):
    def __init__(self, records):
        self.records = records

    def primary_key(self):
        return

    def read_records(self, sync_mode):
        return self.records


class MockPartition(Partition):
    def __init__(self, records):
        self.records = records

    def read(self):
        return self.records

    def to_slice(self):
        return None

    def stream_name(self):
        return "mock_stream"

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return self is other


class MockConcurrentStream:
    name = "mock_stream"
    cursor_field = None
    cursor = None

    def __init__(self, records):
        self.records = records

    def generate_partitions(self):
        yield MockPartition(records=self.records)

    def get_json_schema(self):
        return {}

    def as_airbyte_stream(self):
        return None

    def log_stream_sync_configuration(self):
        return None

    def check_availability(self):
        return StreamAvailability.available()


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


@pytest.mark.parametrize("boards_records, organizations_records, expected_board_ids", test_cases)
def test_read_all_boards(components_module, boards_records, organizations_records, expected_board_ids):
    OrderIdsPartitionRouter = components_module.OrderIdsPartitionRouter
    # Set up mock streams with provided records
    partition_router = OrderIdsPartitionRouter(parent_stream_configs=[None], config=None, parameters=None)
    boards_stream = MockStream(records=boards_records)
    organizations_stream = MockStream(records=organizations_records)

    # Call the function and check the result
    board_ids = list(partition_router.read_all_boards(boards_stream, organizations_stream))
    assert board_ids == expected_board_ids


@pytest.mark.parametrize("boards_records, organizations_records, expected_board_ids", test_cases)
def test_read_all_boards_with_concurrent_parent_streams(components_module, boards_records, organizations_records, expected_board_ids):
    OrderIdsPartitionRouter = components_module.OrderIdsPartitionRouter
    partition_router = OrderIdsPartitionRouter(parent_stream_configs=[None], config=None, parameters=None)
    boards_stream = MockConcurrentStream(records=boards_records)
    organizations_stream = MockConcurrentStream(records=organizations_records)

    board_ids = list(partition_router.read_all_boards(boards_stream, organizations_stream))
    assert board_ids == expected_board_ids
