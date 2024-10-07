#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy


class MockStream:
    def __init__(self, records, exit_on_rate_limit=True):
        self.records = records
        self._exit_on_rate_limit = exit_on_rate_limit
        type(self).exit_on_rate_limit = property(
            lambda self: self._get_exit_on_rate_limit(), lambda self, value: self._set_exit_on_rate_limit(value)
        )

    def _get_exit_on_rate_limit(self):
        return self._exit_on_rate_limit

    def _set_exit_on_rate_limit(self, value):
        self._exit_on_rate_limit = value

    def read_records(self, sync_mode, stream_slice):
        return self.records


@pytest.mark.parametrize(
    "records, stream_slice, exit_on_rate_limit, expected_result, raises_exception",
    [
        ([{"id": 1}], None, True, {"id": 1}, False),  # Single record, with setter
        ([{"id": 1}, {"id": 2}], None, True, {"id": 1}, False),  # Multiple records, with setter
        ([], None, True, None, True),  # No records, with setter
    ],
)
def test_get_first_record_for_slice(records, stream_slice, exit_on_rate_limit, expected_result, raises_exception):
    stream = MockStream(records, exit_on_rate_limit)

    if raises_exception:
        with pytest.raises(StopIteration):
            HttpAvailabilityStrategy().get_first_record_for_slice(stream, stream_slice)
    else:
        result = HttpAvailabilityStrategy().get_first_record_for_slice(stream, stream_slice)
        assert result == expected_result

    assert stream.exit_on_rate_limit == exit_on_rate_limit
