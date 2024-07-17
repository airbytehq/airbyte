#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.utils.stream_helper import get_first_record_for_slice


class MockStream:
    def __init__(self, records):
        self.records = records
        self.rate_limit = False
        self.has_setter = False

    def read_records(self, sync_mode, stream_slice):
        return iter(self.records)  # Simulate returning an iterator

    def is_exit_on_rate_limit(self):
        return self.rate_limit

    def exit_on_rate_limit(self, value):
        if self.has_setter:
            self.rate_limit = value

    def set_has_setter(self, value):
        self.has_setter = value


@pytest.fixture
def mock_stream():
    return MockStream([{'id': 1, 'name': 'Record 1'}, {'id': 2, 'name': 'Record 2'}])


@pytest.mark.parametrize(
    "stream_slice, has_setter, expected",
    [
        ({"start": 0, "count": 1}, True, {'id': 1, 'name': 'Record 1'}),
        (None, True, {'id': 1, 'name': 'Record 1'}),  # Default behavior with stream_slice
        ({"start": 0, "count": 1}, False, {'id': 1, 'name': 'Record 1'}),
        (None, False, {'id': 1, 'name': 'Record 1'})   # Default behavior without stream_slice
    ]
)
def test_get_first_record_for_slice(mock_stream, stream_slice, has_setter, expected):
    mock_stream.set_has_setter(has_setter)
    result = get_first_record_for_slice(mock_stream, stream_slice)
    assert result == expected
