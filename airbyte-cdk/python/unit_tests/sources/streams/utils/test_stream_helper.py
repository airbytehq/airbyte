#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.utils.stream_helper import get_first_record_for_slice


class MockStream:
    def __init__(self, records):
        self.records = records
        self._exit_on_rate_limit = False

    @property
    def exit_on_rate_limit(self):
        return self._exit_on_rate_limit

    @exit_on_rate_limit.setter
    def exit_on_rate_limit(self, value):
        self._exit_on_rate_limit = value

    def read_records(self, sync_mode, stream_slice):
        return iter(self.records)


@pytest.mark.parametrize(
    "stream_input, slice_input, expected_output, expect_exception",
    [
        (MockStream([{'id': 1}, {'id': 2}, {'id': 3}]), None, {'id': 1}, False),  # Basic case
        (MockStream([]), None, None, True),  # Empty records, expect StopIteration
        (MockStream([{'id': 1}, {'id': 2}, {'id': 3}]), {'start': 0, 'count': 2}, {'id': 1}, False),  # With stream slice
    ]
)
def test_get_first_record_for_slice(stream_input, slice_input, expected_output, expect_exception):
    original_exit_on_rate_limit = stream_input.exit_on_rate_limit

    try:
        stream_input.exit_on_rate_limit = True
        if expect_exception:
            with pytest.raises(StopIteration):
                get_first_record_for_slice(stream_input, slice_input)
        else:
            result = get_first_record_for_slice(stream_input, slice_input)
            assert result == expected_output
    finally:
        stream_input.exit_on_rate_limit = original_exit_on_rate_limit
