#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.utils.stream_helper import get_first_record_for_slice


class MockStream:
    def __init__(self, records, exit_on_rate_limit=True, has_setter=False):
        self.records = records
        self._exit_on_rate_limit = exit_on_rate_limit
        if has_setter:
            # Define property with getter and setter if has_setter is True
            type(self).exit_on_rate_limit = property(
                lambda self: self._get_exit_on_rate_limit(),
                lambda self, value: self._set_exit_on_rate_limit(value)
            )
        else:
            self.exit_on_rate_limit = exit_on_rate_limit

    def _get_exit_on_rate_limit(self):
        return self._exit_on_rate_limit

    def _set_exit_on_rate_limit(self, value):
        self._exit_on_rate_limit = value

    def read_records(self, sync_mode, stream_slice):
        return self.records


@pytest.mark.parametrize(
    "records, stream_slice, exit_on_rate_limit, has_setter, expected_result, raises_exception",
    [
        ([{"id": 1}], None, True, False, {"id": 1}, False),  # Single record, no setter
        ([{"id": 1}, {"id": 2}], None, True, False, {"id": 1}, False),  # Multiple records, no setter
        ([], None, True, False, None, True),  # No records, no setter
        ([{"id": 1}], None, True, True, {"id": 1}, False),  # Single record, with setter
        ([{"id": 1}, {"id": 2}], None, True, True, {"id": 1}, False),  # Multiple records, with setter
        ([], None, True, True, None, True),  # No records, with setter
    ]
)
def test_get_first_record_for_slice(records, stream_slice, exit_on_rate_limit, has_setter, expected_result, raises_exception):
    stream = MockStream(records, exit_on_rate_limit, has_setter)

    if raises_exception:
        with pytest.raises(StopIteration):
            get_first_record_for_slice(stream, stream_slice)
    else:
        result = get_first_record_for_slice(stream, stream_slice)
        assert result == expected_result

    if has_setter:
        assert stream.exit_on_rate_limit == exit_on_rate_limit
